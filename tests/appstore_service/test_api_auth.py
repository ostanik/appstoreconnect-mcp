"""Unit tests for appstore_service.api_auth module."""
from unittest.mock import mock_open, patch

from appstore_service.api_auth import AppStoreConnectAuth


def _configure(mock_config):
    mock_config.KEY_ID = "test_key_id"
    mock_config.ISSUER_ID = "test_issuer_id"
    mock_config.PRIVATE_KEY_PATH = "test_path.p8"
    mock_config.EXPIRATION_MINUTES = 19


class TestAppStoreConnectAuth:
    """Test cases for AppStoreConnectAuth class."""

    @patch('appstore_service.api_auth.config')
    def test_init(self, mock_config):
        """Test AppStoreConnectAuth initialization reads config."""
        _configure(mock_config)

        auth = AppStoreConnectAuth()

        assert auth.key_id == "test_key_id"
        assert auth.issuer_id == "test_issuer_id"
        assert auth.private_key_path == "test_path.p8"
        assert auth.expiration_minutes == 19
        assert auth.base_url == "https://api.appstoreconnect.apple.com/v1"

    @patch('appstore_service.api_auth.config')
    @patch('appstore_service.api_auth.jwt.encode')
    @patch('builtins.open', new_callable=mock_open, read_data="fake_private_key")
    @patch('time.time', return_value=1000000)
    def test_token_triggers_jwt_encode_with_expected_payload(
            self, _mock_time, _mock_file, mock_jwt_encode, mock_config):
        """Accessing `.token` when no token cached encodes a new JWT."""
        _configure(mock_config)
        mock_jwt_encode.return_value = "fake_jwt_token"

        auth = AppStoreConnectAuth()
        token = auth.token

        expected_headers = {
            "alg": "ES256",
            "kid": "test_key_id",
            "typ": "JWT"
        }
        expected_payload = {
            "iss": "test_issuer_id",
            "iat": 1000000,
            "exp": 1000000 + (19 * 60),
            "aud": "appstoreconnect-v1"
        }
        mock_jwt_encode.assert_called_once_with(
            expected_payload,
            "fake_private_key",
            algorithm="ES256",
            headers=expected_headers
        )
        assert token == "fake_jwt_token"

    @patch('appstore_service.api_auth.config')
    @patch('appstore_service.api_auth.jwt.encode', return_value="new_token")
    @patch('builtins.open', new_callable=mock_open, read_data="fake_private_key")
    @patch('time.time')
    def test_token_regenerates_when_expired(
            self, mock_time, _mock_file, mock_jwt_encode, mock_config):
        """An expired token triggers regeneration on next access."""
        _configure(mock_config)

        # First access at t=1_000_000 generates the initial token.
        mock_time.return_value = 1_000_000
        auth = AppStoreConnectAuth()
        first = auth.token
        assert first == "new_token"
        assert mock_jwt_encode.call_count == 1

        # Move time past expiration; next access should regenerate.
        mock_time.return_value = 1_000_000 + (19 * 60) + 1
        mock_jwt_encode.return_value = "refreshed_token"
        second = auth.token
        assert second == "refreshed_token"
        assert mock_jwt_encode.call_count == 2

    @patch('appstore_service.api_auth.config')
    @patch('appstore_service.api_auth.jwt.encode', return_value="stable_token")
    @patch('builtins.open', new_callable=mock_open, read_data="fake_private_key")
    @patch('time.time')
    def test_token_cached_while_valid(
            self, mock_time, _mock_file, mock_jwt_encode, mock_config):
        """A still-valid cached token is returned without regenerating."""
        _configure(mock_config)

        mock_time.return_value = 1_000_000
        auth = AppStoreConnectAuth()
        assert auth.token == "stable_token"

        # Advance time but stay within expiration window.
        mock_time.return_value = 1_000_000 + (10 * 60)
        assert auth.token == "stable_token"

        # jwt.encode was called exactly once across both accesses.
        assert mock_jwt_encode.call_count == 1

    @patch('appstore_service.api_auth.config')
    @patch('appstore_service.api_auth.jwt.encode', return_value="test_token")
    @patch('builtins.open', new_callable=mock_open, read_data="fake_private_key")
    @patch('time.time', return_value=1_000_000)
    def test_headers_property(
            self, _mock_time, _mock_file, _mock_jwt_encode, mock_config):
        """`headers` property includes the bearer token and JSON content type."""
        _configure(mock_config)

        auth = AppStoreConnectAuth()
        assert auth.headers == {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }
