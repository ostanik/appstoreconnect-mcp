"""Service for managing App Store Connect app version operations."""
from ._base import BaseService


class VersionService(BaseService):
    """Service for managing App Store Connect app version operations."""

    def create_version(
            self,
            app_id: str,
            version_string: str,
            platform: str = "IOS"):
        """Create a new version for an app."""
        payload = {
            "data": {
                "type": "appStoreVersions",
                "attributes": {
                    "versionString": version_string,
                    "platform": platform
                },
                "relationships": self._app_relationship(app_id),
            }
        }
        return self._post(f"{self.auth.base_url}/appStoreVersions", payload)

    def get_version(self, app_id: str, version_string: str):
        """Get an app store version by version string."""
        url = (f"{self.auth.base_url}/appStoreVersions"
               f"?filter[app]={app_id}&filter[versionString]={version_string}")
        return self._get(url)

    def associate_build_to_version(self, version_id: str, build_id: str):
        """Associate a build with an app version."""
        url = f"{self.auth.base_url}/appStoreVersions/{version_id}/relationships/build"
        payload = {
            "data": {
                "type": "builds",
                "id": build_id
            }
        }
        return self._patch(url, payload)

    def submit_for_review(self, version_id: str):
        """Submit an app version for review."""
        payload = {
            "data": {
                "type": "appStoreVersionSubmissions",
                "relationships": {
                    "appStoreVersion": {
                        "data": {
                            "type": "appStoreVersions",
                            "id": version_id
                        }
                    }
                }
            }
        }
        return self._post(f"{self.auth.base_url}/appStoreVersionSubmissions", payload)

    def release_pending_version(self, version_id: str):
        """Release an approved app version that is pending developer release."""
        payload = {
            "data": {
                "type": "appStoreVersionReleaseRequests",
                "relationships": {
                    "appStoreVersion": {
                        "data": {
                            "type": "appStoreVersions",
                            "id": version_id
                        }
                    }
                }
            }
        }
        return self._post(
            f"{self.auth.base_url}/appStoreVersionReleaseRequests", payload)

    def list(self, app_id: str):
        """List all app store versions for an app."""
        return self._get(f"{self.auth.base_url}/apps/{app_id}/appStoreVersions")
