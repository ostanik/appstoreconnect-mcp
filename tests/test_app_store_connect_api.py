"""Unit tests for app_store_connect_api module."""
import inspect
from unittest.mock import patch

import app_store_connect_api
from appstore_service.app_store import AppStore


class TestAppStoreConnectApi:
    """Test cases for app_store_connect_api functions."""

    @patch('app_store_connect_api.app_store_instance')
    def test_list_apps(self, mock_app_store):
        """Test list_apps function."""
        expected_apps = [{"id": "123", "name": "Test App"}]
        mock_app_store.list_apps.return_value = expected_apps

        result = app_store_connect_api.list_apps()

        mock_app_store.list_apps.assert_called_once()
        assert result == expected_apps

    @patch('app_store_connect_api.app_store_instance')
    def test_get_app_info_success(self, mock_app_store):
        """Test get_app_info with valid bundle_id."""
        bundle_id = "com.example.test"
        expected_info = {"id": "123", "bundleId": bundle_id}
        mock_app_store.get_app_info.return_value = expected_info

        result = app_store_connect_api.get_app_info(bundle_id)

        mock_app_store.get_app_info.assert_called_once_with(bundle_id)
        assert result == expected_info

    def test_get_app_info_missing_bundle_id(self):
        """Test get_app_info with missing bundle_id."""
        result, status_code = app_store_connect_api.get_app_info(None)

        assert result == {"error": "Missing required parameter: bundleId"}
        assert status_code == 400

    def test_get_app_info_empty_bundle_id(self):
        """Test get_app_info with empty bundle_id."""
        result, status_code = app_store_connect_api.get_app_info("")

        assert result == {"error": "Missing required parameter: bundleId"}
        assert status_code == 400

    @patch('app_store_connect_api.app_store_instance')
    def test_list_beta_groups_success(self, mock_app_store):
        """Test list_beta_groups with valid bundle_id."""
        bundle_id = "com.example.test"
        expected_groups = [{"id": "group1", "name": "Internal Testers"}]
        mock_app_store.get_beta_groups.return_value = expected_groups

        result = app_store_connect_api.list_beta_groups(bundle_id)

        mock_app_store.get_beta_groups.assert_called_once_with(bundle_id)
        assert result == expected_groups

    def test_list_beta_groups_missing_bundle_id(self):
        """Test list_beta_groups with missing bundle_id."""
        result, status_code = app_store_connect_api.list_beta_groups(None)

        assert result == {"error": "Missing required parameter: bundleId"}
        assert status_code == 400

    @patch('app_store_connect_api.app_store_instance')
    def test_list_testers_in_group_success(self, mock_app_store):
        """Test list_testers_in_group with valid group_id."""
        group_id = "group123"
        expected_testers = [{"id": "tester1", "email": "test@example.com"}]
        mock_app_store.list_testers_in_group.return_value = expected_testers

        result = app_store_connect_api.list_testers_in_group(group_id)

        mock_app_store.list_testers_in_group.assert_called_once_with(group_id)
        assert result == expected_testers

    def test_list_testers_in_group_missing_group_id(self):
        """Test list_testers_in_group with missing group_id."""
        result, status_code = app_store_connect_api.list_testers_in_group(None)

        assert result == {"error": "Missing required parameter: groupId"}
        assert status_code == 400

    @patch('app_store_connect_api.app_store_instance')
    def test_list_builds_success(self, mock_app_store):
        """Test list_builds with valid bundle_id."""
        bundle_id = "com.example.test"
        expected_builds = [{"id": "build1", "version": "1.0.0"}]
        mock_app_store.get_builds.return_value = expected_builds

        result = app_store_connect_api.list_builds(bundle_id)

        mock_app_store.get_builds.assert_called_once_with(bundle_id)
        assert result == expected_builds

    def test_list_builds_missing_bundle_id(self):
        """Test list_builds with missing bundle_id."""
        result, status_code = app_store_connect_api.list_builds(None)

        assert result == {"error": "Missing required parameter: bundleId"}
        assert status_code == 400

    def test_list_builds_empty_bundle_id(self):
        """Test list_builds with empty bundle_id."""
        result, status_code = app_store_connect_api.list_builds("")

        assert result == {"error": "Missing required parameter: bundleId"}
        assert status_code == 400

    def test_release_version_accepts_platform_kwarg(self):
        """Regression: AppStore.release_version must accept `platform=` kwarg.

        The MCP dispatcher in app_store_connect_server.py passes platform=
        as a keyword argument. A prior bug named the parameter `_platform`,
        which raised TypeError when called via the full MCP chain from
        unit tests or alternate entry points.
        """
        sig = inspect.signature(AppStore.release_version)
        # bind raises TypeError if the kwarg is not accepted; not raising is the assertion
        sig.bind(None, "com.example.app", "1.0.0", "42", platform="IOS")

    @patch('app_store_connect_api.app_store_instance')
    def test_submit_for_review_success(self, mock_app_store):
        """Test submit_for_review with valid params delegates to AppStore."""
        bundle_id = "com.example.test"
        version = "1.2.3"
        expected = {"data": {"id": "sub-1", "type": "appStoreVersionSubmissions"}}
        mock_app_store.submit_for_review.return_value = expected

        result = app_store_connect_api.submit_for_review(bundle_id, version)

        mock_app_store.submit_for_review.assert_called_once_with(bundle_id, version)
        assert result == expected

    def test_submit_for_review_missing_bundle_id(self):
        """Test submit_for_review rejects missing bundle_id."""
        result, status_code = app_store_connect_api.submit_for_review(None, "1.2.3")

        assert result == {"error": "Missing required parameters: bundleId, version"}
        assert status_code == 400

    def test_submit_for_review_missing_version(self):
        """Test submit_for_review rejects missing version."""
        result, status_code = app_store_connect_api.submit_for_review("com.example.test", None)

        assert result == {"error": "Missing required parameters: bundleId, version"}
        assert status_code == 400
