"""Service for managing App Store Connect build operations."""
from ._base import BaseService


class BuildService(BaseService):
    """Service for managing App Store Connect build operations."""

    def list_builds(self, app_id: str):
        """
        Fetch a list of builds for a specific app.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/builds
        ?filter[app]={APP_ID}&include=preReleaseVersion
        """
        url = f"{self.auth.base_url}/builds?filter[app]={app_id}&include=preReleaseVersion&limit=50"
        return self.get_json(url)

    def get_build_details(self, build_id: str):
        """
        Fetch details for a specific build.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/builds/{build_id}
        """
        return self.get_json(f"{self.auth.base_url}/builds/{build_id}")
