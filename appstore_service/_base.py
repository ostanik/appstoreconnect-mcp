"""Shared base class for App Store Connect service wrappers."""
import requests

from .api_auth import AppStoreConnectAuth

REQUEST_TIMEOUT = 30


class BaseService:
    """Encapsulates HTTP I/O against the App Store Connect API.

    Subclasses use `get_json` / `post_json` / `patch_json` / `delete_status`
    to make authenticated requests against the configured `auth` instance.
    """

    def __init__(self, auth: AppStoreConnectAuth):
        self.auth = auth

    def get_json(self, url, headers=None):
        """GET `url` and return the decoded JSON body."""
        response = requests.get(
            url,
            headers=headers if headers is not None else self.auth.headers,
            timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def post_json(self, url, payload):
        """POST `payload` as JSON and return the decoded JSON body."""
        response = requests.post(
            url,
            headers=self.auth.headers,
            json=payload,
            timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def patch_json(self, url, payload):
        """PATCH `payload` as JSON and return the decoded JSON body."""
        response = requests.patch(
            url,
            headers=self.auth.headers,
            json=payload,
            timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def delete_status(self, url, payload=None):
        """DELETE `url` and return the response status code."""
        response = requests.delete(
            url,
            headers=self.auth.headers,
            json=payload,
            timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.status_code

    @staticmethod
    def app_relationship(app_id):
        """Return the JSON:API relationship block pointing at `app_id`."""
        return {"app": {"data": {"type": "apps", "id": app_id}}}
