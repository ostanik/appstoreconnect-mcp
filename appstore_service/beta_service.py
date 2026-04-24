"""Service for managing App Store Connect beta testing operations."""
from ._base import BaseService


class BetaService(BaseService):
    """Service for managing App Store Connect beta testing functionality."""

    def fetch_beta_groups(self, app_id: str):
        """Fetch a list of beta groups for a specific app."""
        return self._get(f"{self.auth.base_url}/betaGroups?filter[app]={app_id}")

    def add_tester_to_groups(
            self,
            email: str,
            group_ids: list,
            first_name: str = None,
            last_name: str = None):
        """Add a new beta tester and assign them to specified beta groups."""
        group_data = [{"type": "betaGroups", "id": group_id}
                      for group_id in group_ids]

        attributes = {"email": email}
        if first_name:
            attributes["firstName"] = first_name
        if last_name:
            attributes["lastName"] = last_name

        payload = {
            "data": {
                "type": "betaTesters",
                "attributes": attributes,
                "relationships": {
                    "betaGroups": {
                        "data": group_data
                    }
                }
            }
        }
        return self._post(f"{self.auth.base_url}/betaTesters", payload)

    def _get_beta_tester_id_by_email(self, email: str, app_id: str):
        """Find a beta tester's ID by email for a specific app."""
        url = f"{self.auth.base_url}/betaTesters?filter[email]={email}&filter[apps]={app_id}"
        data = self._get(url)
        if data.get("data"):
            return data["data"][0]["id"]
        return None

    def remove_tester_from_groups(
            self,
            email: str,
            group_ids: list,
            app_id: str):
        """Remove a beta tester from specified beta groups."""
        tester_id = self._get_beta_tester_id_by_email(email, app_id)
        if not tester_id:
            return False

        url = f"{self.auth.base_url}/betaTesters/{tester_id}/relationships/betaGroups"
        payload = {
            "data": [{"type": "betaGroups", "id": group_id} for group_id in group_ids]
        }
        status_code = self._delete(url, payload)
        return status_code == 204

    def list_beta_testers(self, app_id: str):
        """List all beta testers for a specific app."""
        return self._get(f"{self.auth.base_url}/betaTesters?filter[apps]={app_id}")

    def list_testers_in_group(self, group_id: str):
        """Fetch a list of beta testers from a specific beta group."""
        return self._get(f"{self.auth.base_url}/betaGroups/{group_id}/betaTesters")

    def create_beta_group(self, app_id: str, name: str):
        """Create a new beta group for a specific app."""
        payload = {
            "data": {
                "type": "betaGroups",
                "attributes": {"name": name},
                "relationships": self._app_relationship(app_id),
            }
        }
        return self._post(f"{self.auth.base_url}/betaGroups", payload)
