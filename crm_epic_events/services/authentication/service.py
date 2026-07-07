import contextlib
import json
import uuid

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

import bcrypt

from jwt import ExpiredSignatureError, decode, encode
from jwt import InvalidTokenError as JWTInvalidTokenError
from sqlalchemy.orm.exc import NoResultFound

from crm_epic_events.config import Config
from crm_epic_events.errors import CustomInvalidCredentialsError, CustomInvalidTokenError
from crm_epic_events.models.user import User
from crm_epic_events.utils import print_success

from .schemas import AccessTokenPayload, RefreshTokenPayload


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AuthTokensService:
    @staticmethod
    def _resolve_token_file(for_lockout: bool = False) -> Path:
        """
        Returns the token file path based on APP_ENV.
        - 'local': writes inside the app directory (visible via bind mount in Docker)
        - anything else ('prod', unset...): writes in the user config directory
        """
        file_name = ".session.json" if not for_lockout else ".lockout.json"
        if Config.APP_ENV == "local":
            return Path("/usr/src/app") / file_name
        return Path.home() / ".config" / "crm_epic_events" / file_name

    @staticmethod
    def generate_access_token(user: "User") -> str:
        payload = AccessTokenPayload(
            id=user.id,
            email=user.email,
            role=user.role,
            exp=datetime.now(UTC) + timedelta(minutes=Config.ACCESS_TOKEN_LIFETIME),
        )
        return encode(payload.model_dump(mode="json"), Config.SECRET_KEY, algorithm=Config.AUTH_ALGORITHM)

    @staticmethod
    def generate_refresh_token(user: "User") -> str:
        payload = RefreshTokenPayload(
            id=user.id,
            exp=datetime.now(UTC) + timedelta(days=Config.REFRESH_TOKEN_LIFETIME),
        )
        return encode(payload.model_dump(mode="json"), Config.SECRET_KEY, algorithm=Config.AUTH_ALGORITHM)

    @classmethod
    def save_tokens(cls, access_token: str, refresh_token: str) -> None:
        token_file = cls._resolve_token_file()
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(
            json.dumps(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
        )

    @classmethod
    def load_tokens(cls) -> dict | None:
        token_file = cls._resolve_token_file()
        if not token_file.exists():
            return None
        try:
            return json.loads(token_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    @classmethod
    def clear_tokens(cls) -> None:
        token_file = cls._resolve_token_file()
        if token_file.exists():
            token_file.unlink()

    @classmethod
    def save_lockout(cls, duration_seconds: int) -> None:
        token_file = cls._resolve_token_file(for_lockout=True)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if token_file.exists():
            with contextlib.suppress(json.JSONDecodeError, OSError):
                existing = json.loads(token_file.read_text())
        existing["locked_until"] = (datetime.now(UTC) + timedelta(seconds=duration_seconds)).isoformat()
        token_file.write_text(json.dumps(existing))

    @classmethod
    def get_lockout_remaining(cls) -> int:
        """Returns the number of seconds remaining in lockout, or 0 if not locked."""
        token_file = cls._resolve_token_file(for_lockout=True)
        if not token_file.exists():
            return 0
        try:
            data = json.loads(token_file.read_text())
            locked_until = data.get("locked_until")
            if not locked_until:
                return 0
            remaining = (datetime.fromisoformat(locked_until) - datetime.now(UTC)).total_seconds()
            return max(0, int(remaining))
        except (json.JSONDecodeError, OSError, ValueError):
            return 0

    @classmethod
    def clear_lockout(cls) -> None:
        token_file = cls._resolve_token_file(for_lockout=True)
        if not token_file.exists():
            return
        try:
            data = json.loads(token_file.read_text())
            data.pop("locked_until", None)
            token_file.write_text(json.dumps(data))
        except (json.JSONDecodeError, OSError):
            pass


class AuthService:
    # factice hash to prevent timing attacks even if user doesn't exist
    # store as a constant class attribute to avoid recomputing it every time
    _FACTICE_PASSWORD = bcrypt.hashpw(str(uuid.uuid4()).encode(), bcrypt.gensalt())

    @staticmethod
    def login(email: str, password: str, db: "Session") -> "User":
        try:
            user = User.get_by_email(email, db)
        except NoResultFound:
            user = None

        # factice hash to prevent timing attacks even if user doesn't exist
        if user is None:
            bcrypt.checkpw(
                password.encode(),
                AuthService._FACTICE_PASSWORD,
            )
            are_credentials_valid = False
        else:
            are_credentials_valid = bcrypt.checkpw(
                password.encode(),
                user.password.encode(),
            )

        if not are_credentials_valid:
            raise CustomInvalidCredentialsError()

        access_token = AuthTokensService.generate_access_token(user)
        refresh_token = AuthTokensService.generate_refresh_token(user)
        AuthTokensService.save_tokens(access_token, refresh_token)

        return user

    @staticmethod
    def logout() -> None:
        AuthTokensService.clear_tokens()
        print_success("Logged out successfully")

    @classmethod
    def get_current_user(cls, db) -> "User | None ":
        """
        Returns the authenticated user from the access token.
        Attempts a silent refresh if the access token is expired.
        Returns None if not authenticated at all.
        """
        tokens = AuthTokensService.load_tokens()
        if not tokens:
            return None
        try:
            payload = decode(tokens["access_token"], Config.SECRET_KEY, algorithms=[Config.AUTH_ALGORITHM])
            return User.get_by_id(payload["id"], db)
        except ExpiredSignatureError:
            return cls._refresh(tokens, db)
        except NoResultFound:
            AuthTokensService.clear_tokens()
            raise CustomInvalidTokenError(message="Session refers to a deleted user.") from None
        except JWTInvalidTokenError:
            raise CustomInvalidTokenError() from None

    @staticmethod
    def _refresh(tokens: dict, db: "Session") -> "User | None":
        """
        Silently issues a new access token using the refresh token.
        Returns the User if successful, None if refresh token is also expired.
        """
        try:
            payload = decode(tokens["refresh_token"], Config.SECRET_KEY, algorithms=[Config.AUTH_ALGORITHM])
            user = User.get_by_id(payload["id"], db)
            new_access_token = AuthTokensService.generate_access_token(user)
            AuthTokensService.save_tokens(new_access_token, tokens["refresh_token"])
            return user
        except NoResultFound:
            AuthTokensService.clear_tokens()
            return None
        except (ExpiredSignatureError, JWTInvalidTokenError):
            AuthTokensService.clear_tokens()
            return None
