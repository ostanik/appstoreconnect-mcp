#!/usr/bin/env python3
"""Main AppStore class for orchestrating App Store Connect API operations."""
import argparse
import json
import sys
import requests

from appstore_service import api_auth
from appstore_service import build_service
from appstore_service import beta_service
from appstore_service import app_info_service
from appstore_service import version_service
from appstore_service import performance_service


class AppStore:
    """Main class for interacting with the App Store Connect API."""

    def __init__(self):
        self.auth = api_auth.AppStoreConnectAuth()
        self.app_info_service = app_info_service.AppInfoService(self.auth)
        self.build_service = build_service.BuildService(self.auth)
        self.beta_service = beta_service.BetaService(self.auth)
        self.version_service = version_service.VersionService(self.auth)
        self.performance_service = performance_service.PerformanceService(
            self.auth)

    def _handle_error(self, err):
        """Centralized error handler to return JSON."""
        print(f"An HTTP error occurred: {err}", file=sys.stderr)
        if err.response is not None:
            print(f"Response body: {err.response.text}", file=sys.stderr)
            try:
                return err.response.json()
            except json.JSONDecodeError:
                return {
                    "error": "HTTP Error",
                    "status_code": err.response.status_code,
                    "text": err.response.text}
        return {"error": str(err)}

    def list_apps(self):
        """Get a list of all apps."""
        try:
            return self.app_info_service.list_apps()
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def get_app_info(self, bundle_id):
        """Get detailed information for a specific app."""
        try:
            return self.app_info_service.get_app_info(bundle_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def get_builds(self, bundle_id):
        """Get list of builds."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {"error": f"App with bundle ID {bundle_id} not found."}
            return self.build_service.list_builds(app_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def get_beta_groups(self, bundle_id):
        """Get a list of beta groups for a specific app."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {"error": f"App with bundle ID {bundle_id} not found."}
            return self.beta_service.fetch_beta_groups(app_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def list_testers_in_group(self, group_id):
        """Get a list of beta testers in a specific group."""
        try:
            return self.beta_service.list_testers_in_group(group_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def add_tester_to_group(self, email, group_id):
        """Add a beta tester to a group."""
        try:
            # Note: add_tester_to_groups from beta_service can handle multiple
            # groups
            return self.beta_service.add_tester_to_groups(email, [group_id])
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def remove_tester_from_group(self, email, group_id, bundle_id):
        """Remove a beta tester from a group."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {"error": f"App with bundle ID {bundle_id} not found."}
            # Note: remove_tester_from_groups from beta_service can handle
            # multiple groups
            return self.beta_service.remove_tester_from_groups(
                email, [group_id], app_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def get_performance_metrics(self, bundle_id):
        """Get performance metrics for a specific app."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {"error": f"App with bundle ID {bundle_id} not found."}
            return self.performance_service.get_perf_power_metrics(app_id)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def release_version(
            self,
            bundle_id,
            version_string,
            build_number,
            _platform="IOS"):
        """Creates a new version, assigns a build and submits it for review."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {
                    "error": f"Could not find app with bundle ID {bundle_id}"}

            build_id = self._find_build_id(
                app_id, version_string, build_number)
            if not build_id:
                return {
                    "error": f"Could not find build for version {version_string} "
                             f"and build number {build_number}"}

            version_info = self._find_version_info(app_id, version_string)
            if not version_info:
                return {
                    "error": f"Version {version_string} not found. "
                             f"Please create it on App Store Connect first."}

            return self._handle_version_state(version_info, build_id)

        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)

    def _find_build_id(self, app_id, version_string, build_number):
        """Helper method to find build ID by version string and build number."""
        builds = self.build_service.list_builds(app_id)

        if not builds or 'data' not in builds:
            return None

        pre_release_versions = {
            item['id']: item['attributes']
            for item in builds.get('included', [])
            if item['type'] == 'preReleaseVersions'
        }

        for build in builds['data']:
            attributes = build.get('attributes', {})
            relationships = build.get('relationships', {})

            pre_release_version_ref = relationships.get(
                'preReleaseVersion', {}).get('data')
            if not pre_release_version_ref:
                continue

            pre_release_version_id = pre_release_version_ref.get('id')
            pre_release_version_attrs = pre_release_versions.get(
                pre_release_version_id)

            if not pre_release_version_attrs:
                continue

            build_v = attributes.get('version')
            marketing_v = pre_release_version_attrs.get('version')

            if build_v == build_number and marketing_v == version_string:
                return build['id']
        return None

    def _find_version_info(self, app_id, version_string):
        """Helper method to find version info by version string."""
        all_versions = self.version_service.list(app_id)
        if all_versions and 'data' in all_versions:
            for v in all_versions['data']:
                if v['attributes']['versionString'] == version_string:
                    return v
        return None

    def _handle_version_state(self, version_info, build_id):
        """Helper method to handle different version states."""
        version_id = version_info['id']
        version_state = version_info['attributes']['appStoreState']

        # Take action based on the version's current state
        if version_state == "PREPARE_FOR_SUBMISSION":
            self.version_service.associate_build_to_version(
                version_id, build_id)
            return self.version_service.submit_for_review(version_id)

        if version_state == "PENDING_DEVELOPER_RELEASE":
            return self.version_service.release_pending_version(version_id)

        if version_state == "WAITING_FOR_REVIEW":
            # Assuming build is already associated, or we could add it here
            # as well
            return {
                "status": "Already in 'WAITING_FOR_REVIEW' state. No action taken."}

        if version_state == "READY_FOR_SALE":
            return {
                "status": "Version is already 'READY_FOR_SALE'. No action taken."}

        return {
            "error": f"Version is in an unhandled state: '{version_state}'. No action taken."}

    def create_beta_group(self, name, bundle_id):
        """Create a new beta group."""
        try:
            app_id = self.app_info_service.get_app_id_by_bundle_id(bundle_id)
            if not app_id:
                return {"error": f"App with bundle ID {bundle_id} not found."}
            return self.beta_service.create_beta_group(app_id, name)
        except requests.exceptions.HTTPError as err:
            return self._handle_error(err)


def main():
    """Command-line interface for App Store Connect API operations."""
    parser = argparse.ArgumentParser(
        description="Interact with the App Store Connect API.")
    subparsers = parser.add_subparsers(dest="action", required=True)

    # Get app info
    parser_get_app = subparsers.add_parser(
        "get_app_info", help="Get information for a specific app.")
    parser_get_app.add_argument("bundle_id", help="The bundle ID of the app.")

    # List builds
    parser_list_builds = subparsers.add_parser(
        "list_builds", help="List all builds for an app.")
    parser_list_builds.add_argument(
        "bundle_id", help="The bundle ID of the app.")

    # Release version
    parser_release = subparsers.add_parser(
        "release_version", help="Release a new version of an app.")
    parser_release.add_argument("bundle_id", help="The bundle ID of the app.")
    parser_release.add_argument("version_string",
                                help="The version string (e.g., '1.2.3').")
    parser_release.add_argument("build_number", help="The build number.")
    parser_release.add_argument(
        "--platform",
        default="IOS",
        help="The platform (e.g., IOS, MAC_OS, TV_OS). Defaults to IOS.")

    args = parser.parse_args()
    appstore = AppStore()

    data = None
    if args.action == "list_apps":
        data = appstore.list_apps()
    elif args.action == "get_app_info":
        data = appstore.get_app_info(args.bundle_id)
    elif args.action == "list_builds":
        data = appstore.get_builds(args.bundle_id)
    elif args.action == "release_version":
        data = appstore.release_version(
            args.bundle_id,
            args.version_string,
            args.build_number,
            args.platform)

    if data:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
