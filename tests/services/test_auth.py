# tests/services/authentication/test_service.py
from unittest.mock import patch

import pytest

from sqlalchemy.exc import NoResultFound

from crm_epic_events.errors import CustomInvalidCredentialsError, CustomInvalidTokenError
from crm_epic_events.models import User
from crm_epic_events.services.authentication.service import AuthService, AuthTokensService
from tests.factories import SECURED_RAW_PASSWORD


# ── login ────────────────────────────────────────────────────────────────────


class TestLogin:
    def test_login_success(self, user, mock_db):
        with (
            patch.object(User, "get_by_email", return_value=user),
        ):
            result = AuthService.login(user.email, SECURED_RAW_PASSWORD, mock_db)

        assert result == user
        tokens = AuthTokensService.load_tokens()
        assert tokens is not None
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    def test_login_wrong_password(self, user, mock_db):
        with (
            patch.object(User, "get_by_email", return_value=user),
            pytest.raises(CustomInvalidCredentialsError),
        ):
            AuthService.login(user.email, "wrong_password", mock_db)

    def test_login_unknown_email(self, mock_db):
        with (
            patch.object(User, "get_by_email", side_effect=NoResultFound()),
            pytest.raises(CustomInvalidCredentialsError),
        ):
            AuthService.login("ghost@test.com", SECURED_RAW_PASSWORD, mock_db)


# ── get_current_user ──────────────────────────────────────────────────────────


class TestGetCurrentUser:
    def test_returns_none_when_no_tokens(self, mock_db):
        result = AuthService.get_current_user(mock_db)
        assert not result

    def test_valid_access_token(self, user, mock_db, access_token, refresh_token):
        AuthTokensService.save_tokens(
            access_token(user),
            refresh_token(user),
        )
        with patch.object(User, "get_by_id", return_value=user):
            result = AuthService.get_current_user(mock_db)

        assert result == user

    def test_expired_access_token_triggers_refresh(self, user, mock_db, access_token, refresh_token):
        AuthTokensService.save_tokens(
            access_token(user, expired=True),
            refresh_token(user),
        )
        with patch.object(User, "get_by_id", return_value=user):
            result = AuthService.get_current_user(mock_db)

        assert result == user

    def test_invalid_token_raises(self, mock_db):
        AuthTokensService.save_tokens("wrong.token.1", "wrong.token.2")
        with pytest.raises(CustomInvalidTokenError):
            AuthService.get_current_user(mock_db)


# ── _refresh ──────────────────────────────────────────────────────────────────


class TestRefresh:
    def test_refresh_success(self, user, mock_db, access_token, refresh_token):
        tokens = {
            "access_token": access_token(user, expired=True),
            "refresh_token": refresh_token(user),
        }
        with patch.object(User, "get_by_id", return_value=user):
            result = AuthService._refresh(tokens, mock_db)

        assert result == user
        new_tokens = AuthTokensService.load_tokens()
        assert new_tokens["refresh_token"] == tokens["refresh_token"]  # refresh token inchangé

    def test_refresh_expired_refresh_token_clears_tokens(self, user, mock_db, access_token, refresh_token):
        tokens = {
            "access_token": access_token(user, expired=True),
            "refresh_token": refresh_token(user, expired=True),
        }
        AuthTokensService.save_tokens(tokens["access_token"], tokens["refresh_token"])

        result = AuthService._refresh(tokens, mock_db)

        assert result is None
        assert AuthTokensService.load_tokens() is None  # tokens supprimés


# ── logout ────────────────────────────────────────────────────────────────────


class TestLogout:
    def test_logout_clears_tokens(self, user, access_token, refresh_token):
        AuthTokensService.save_tokens(
            access_token(user),
            refresh_token(user),
        )
        with (
            patch("crm_epic_events.services.authentication.service.print_success"),
            patch("crm_epic_events.services.authentication.service.exit_app"),
        ):
            AuthService.logout()

        assert AuthTokensService.load_tokens() is None

    def test_logout_prints_success_message(self, user, access_token, refresh_token):
        AuthTokensService.save_tokens(
            access_token(user),
            refresh_token(user),
        )
        with (
            patch("crm_epic_events.services.authentication.service.print_success") as mock_print,
            patch("crm_epic_events.services.authentication.service.exit_app"),
        ):
            AuthService.logout()

        mock_print.assert_called_once_with("Logged out successfully")

    def test_logout_exits_app(self, user, access_token, refresh_token):
        AuthTokensService.save_tokens(
            access_token(user),
            refresh_token(user),
        )
        with (
            patch("crm_epic_events.services.authentication.service.print_success"),
            patch("crm_epic_events.services.authentication.service.exit_app") as mock_exit,
        ):
            AuthService.logout()

        mock_exit.assert_called_once()
