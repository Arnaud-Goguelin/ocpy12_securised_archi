from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from crm_epic_events.services.authentication.service import AuthTokensService
from tests.factories import UserFactory


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def access_token():
    def _make(user, expired: bool = False) -> str:
        with patch("crm_epic_events.services.authentication.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=UTC) if expired else datetime.now(UTC)
            token = AuthTokensService.generate_access_token(user)
            return token

    return _make


@pytest.fixture
def refresh_token():
    def _make(user, expired: bool = False) -> str:
        with patch("crm_epic_events.services.authentication.service.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, tzinfo=UTC) if expired else datetime.now(UTC)
            token = AuthTokensService.generate_refresh_token(user)
            return token

    return _make


@pytest.fixture(autouse=True)
def clear_tokens():
    """Ensure no leftover token file between tests."""
    AuthTokensService.clear_tokens()
    yield
    AuthTokensService.clear_tokens()
