"""Unit tests for appstore_service.app_info_service module."""
from unittest.mock import Mock, patch

import pytest
import requests

from appstore_service._base import REQUEST_TIMEOUT
from appstore_service.app_info_service import AppInfoService


class TestAppInfoService:
    """Test cases for AppInfoService class."""

    mock_auth: Mock
    service: AppInfoService

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth = Mock()
        self.mock_auth.base_url = "https://api.appstoreconnect.apple.com/v1"
        self.mock_auth.headers = {"Authorization": "Bearer test_token"}
        self.service = AppInfoService(self.mock_auth)

    @patch('requests.get')
    def test_list_apps_success(self, mock_get):
        """Test successful apps listing."""
        expected_response = {
            "data": [
                {"id": "123", "type": "apps", "attributes": {"name": "Test App"}}
            ]
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.service.list_apps()

        mock_get.assert_called_once_with(
            "https://api.appstoreconnect.apple.com/v1/apps",
            headers={"Authorization": "Bearer test_token"},
            timeout=REQUEST_TIMEOUT
        )
        assert result == expected_response

    @patch('requests.get')
    def test_list_apps_http_error(self, mock_get):
        """Test list_apps handles HTTP errors properly."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            self.service.list_apps()

    @patch('requests.get')
    def test_get_app_info_success(self, mock_get):
        """Test successful app info retrieval."""
        bundle_id = "com.example.testapp"
        expected_response = {
            "data": [
                {
                    "id": "123",
                    "type": "apps",
                    "attributes": {
                        "bundleId": bundle_id,
                        "name": "Test App"
                    }
                }
            ]
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.service.get_app_info(bundle_id)

        mock_get.assert_called_once_with(
            f"https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]={bundle_id}",
            headers={"Authorization": "Bearer test_token"},
            timeout=REQUEST_TIMEOUT
        )
        assert result == expected_response["data"][0]

    @patch('requests.get')
    def test_get_app_info_not_found(self, mock_get):
        """Test get_app_info when app is not found."""
        bundle_id = "com.example.nonexistent"
        expected_response = {"data": []}

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.service.get_app_info(bundle_id)

        assert result == {"error": "App not found"}

    @patch('requests.get')
    def test_get_app_info_http_error(self, mock_get):
        """Test get_app_info handles HTTP errors properly."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            self.service.get_app_info("com.example.test")

    @patch.object(AppInfoService, 'get_app_info')
    def test_get_app_id_by_bundle_id_success(self, mock_get_app_info):
        """Test successful app ID retrieval by bundle ID."""
        bundle_id = "com.example.testapp"
        mock_get_app_info.return_value = {
            "id": "123",
            "attributes": {"bundleId": bundle_id}
        }

        result = self.service.get_app_id_by_bundle_id(bundle_id)

        mock_get_app_info.assert_called_once_with(bundle_id)
        assert result == "123"

    @patch.object(AppInfoService, 'get_app_info')
    def test_get_app_id_by_bundle_id_not_found(self, mock_get_app_info):
        """Test get_app_id_by_bundle_id when app is not found."""
        bundle_id = "com.example.nonexistent"
        mock_get_app_info.return_value = {"error": "App not found"}

        result = self.service.get_app_id_by_bundle_id(bundle_id)

        assert result is None

    @patch.object(AppInfoService, 'get_app_info')
    def test_get_app_id_by_bundle_id_no_id_field(self, mock_get_app_info):
        """Test get_app_id_by_bundle_id when response has no ID field."""
        bundle_id = "com.example.testapp"
        mock_get_app_info.return_value = {
            "attributes": {"bundleId": bundle_id}
            # Missing "id" field
        }

        result = self.service.get_app_id_by_bundle_id(bundle_id)

        assert result is None

    def test_request_timeout_constant(self):
        """Test that REQUEST_TIMEOUT is set to expected value."""
        assert REQUEST_TIMEOUT == 30
