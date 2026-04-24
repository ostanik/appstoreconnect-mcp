"""Service for retrieving App Store Connect app information and metadata."""
from . import config
from ._base import BaseService


class AppInfoService(BaseService):
    """Service for managing App Store Connect app information and metadata operations."""

    def list_apps(self):
        """
        Fetch a list of all apps on the account.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/apps
        """
        return self.get_json(f"{self.auth.base_url}/apps")

    def get_app_info(self, bundle_id: str):
        """
        Fetch detailed information for a specific app by its bundle ID.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/apps?filter[bundleId]={bundle_id}
        """
        url = f"{self.auth.base_url}/apps?filter[bundleId]={bundle_id}"
        data = self.get_json(url)
        if data.get("data"):
            return data["data"][0]
        return {"error": "App not found"}

    def get_app_id_by_bundle_id(self, bundle_id: str):
        """Get the app ID for a given bundle ID."""
        app_info = self.get_app_info(bundle_id)
        if app_info and "id" in app_info:
            return app_info["id"]
        return None

    def fetch_xcode_metrics(self, app_id: str):
        """
        Fetch Xcode (power and performance) metrics for a specific app.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/perfPowerMetrics
        """
        headers = self.auth.headers.copy()
        headers["Accept"] = "application/vnd.apple.xcode-metrics+json, application/json"
        return self.get_json(
            f"{self.auth.base_url}/apps/{app_id}/perfPowerMetrics",
            headers=headers)

    def fetch_customer_reviews(self, app_id: str):
        """
        Fetch customer reviews for a specific app.
        Endpoint: GET https://api.appstoreconnect.apple.com/v1/apps/{APP_ID}/customerReviews
        """
        return self.get_json(f"{self.auth.base_url}/apps/{app_id}/customerReviews")

    def get_latest_editable_app_store_version_id(self, app_id: str):
        """
        Fetches the ID of the latest App Store Version that is in an editable state
        (specifically PREPARE_FOR_SUBMISSION), sorted by version string descending.
        Returns the ID if found, otherwise None.
        """
        url = (f"{self.auth.base_url}/apps/{app_id}/appStoreVersions"
               f"?filter[appStoreState]=PREPARE_FOR_SUBMISSION"
               f"&sort=-versionString&limit=1")
        data = self.get_json(url)
        if data.get("data") and len(data["data"]) > 0:
            version_id = data["data"][0]["id"]
            version_string = data["data"][0]["attributes"]["versionString"]
            platform = data["data"][0]["attributes"]["platform"]
            print(
                f"Found latest editable App Store Version: ID {version_id}, "
                f"Version {version_string}, Platform {platform}.")
            return version_id
        print(
            f"No App Store Version found in 'PREPARE_FOR_SUBMISSION' state "
            f"for app ID {config.APP_ID}.")
        print("Please ensure there is an app version created in App Store Connect "
              "that is ready for build assignment.")
        return None
