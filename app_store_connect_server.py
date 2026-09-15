#!/usr/bin/env python3
"""App Store Connect MCP Server.

This module implements an MCP (Model Context Protocol) server that provides
tools for interacting with the App Store Connect API.
"""
import os
import sys
import json
import logging
from pathlib import Path
import app_store_connect_api as api

# Change to the correct working directory
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR)

# Get the absolute path for the log file
LOG_FILE = SCRIPT_DIR / "logs" / "app_store_connect_server.log"

# Ensure the log directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stderr)
    ]
)

# Log startup information
logging.info("Script started at %s", os.getcwd())
logging.info("Log file location: %s", LOG_FILE)
logging.info("Script location: %s", __file__)


def handle_initialize(message):
    """Handle the initialize message from Cursor."""
    return {
        "jsonrpc": "2.0",
        "id": message.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "enabled": True
                }
            },
            "serverInfo": {
                "name": "app-store-connect-services",
                "version": "1.0.1"
            }
        }
    }


def handle_tools_list(message):
    """Handle the tools/list message from Cursor."""
    return {
        "jsonrpc": "2.0",
        "id": message.get("id"),
        "result": {
            "tools": [
                {
                    "name": "app-store-connect_list-apps",
                    "description": "List all apps in App Store Connect",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "app-store-connect_get-app-info",
                    "description": "Get detailed information about an app",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            }
                        },
                        "required": ["bundleId"]
                    }
                },
                {
                    "name": "app-store-connect_list-beta-groups",
                    "description": "List all beta groups for an app",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            }
                        },
                        "required": ["bundleId"]
                    }
                },
                {
                    "name": "app-store-connect_list-testers-in-group",
                    "description": "List all beta testers in a specific group",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "groupId": {
                                "type": "string",
                                "description": "The ID of the beta group"
                            }
                        },
                        "required": ["groupId"]
                    }
                },
                {
                    "name": "app-store-connect_list-builds",
                    "description": "List all builds for an app",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            }
                        },
                        "required": ["bundleId"]
                    }
                },
                {
                    "name": "app-store-connect_submit-for-review",
                    "description": "Submit an app version for review",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            },
                            "version": {
                                "type": "string",
                                "description": "The version string to submit (e.g., '1.2.3')"
                            }
                        },
                        "required": ["bundleId", "version"]
                    }
                },
                {
                    "name": "app-store-connect_create-beta-group",
                    "description": "Create a new beta group",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the beta group"
                            },
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app to create the group for"
                            }
                        },
                        "required": ["name", "bundleId"]
                    }
                },
                {
                    "name": "app-store-connect_add-beta-tester-to-group",
                    "description": "Add a beta tester to a group",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "The tester's email address"
                            },
                            "groupId": {
                                "type": "string",
                                "description": "The ID of the beta group"
                            }
                        },
                        "required": ["email", "groupId"]
                    }
                },
                {
                    "name": "app-store-connect_release-version",
                    "description": "Release a new version of an app",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            },
                            "version": {
                                "type": "string",
                                "description": "The version string to release (e.g., '1.2.3')"
                            },
                            "buildNumber": {
                                "type": "string",
                                "description": "The build number corresponding to the version"
                            },
                            "platform": {
                                "type": "string",
                                "description": "The platform of the app (e.g., 'IOS', 'MAC_OS'). "
                                "Defaults to 'IOS'."
                            }
                        },
                        "required": ["bundleId", "version", "buildNumber"]
                    }
                },
                {
                    "name": "app-store-connect_get-performance-metrics",
                    "description": "Get performance metrics for an app",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "bundleId": {
                                "type": "string",
                                "description": "The bundle ID of the app"
                            }
                        },
                        "required": ["bundleId"]
                    }
                }
            ]
        }
    }


TOOL_DISPATCH = {
    "app-store-connect_list-apps": lambda args: api.list_apps(),
    "app-store-connect_get-app-info": lambda args: api.get_app_info(
        bundle_id=args.get("bundleId")),
    "app-store-connect_list-beta-groups": lambda args: api.list_beta_groups(
        bundle_id=args.get("bundleId")),
    "app-store-connect_list-testers-in-group": lambda args: api.list_testers_in_group(
        group_id=args.get("groupId")),
    "app-store-connect_list-builds": lambda args: api.list_builds(
        bundle_id=args.get("bundleId")),
    "app-store-connect_submit-for-review": lambda args: api.submit_for_review(
        bundle_id=args.get("bundleId"),
        version=args.get("version")),
    "app-store-connect_create-beta-group": lambda args: api.create_beta_group(
        name=args.get("name"),
        bundle_id=args.get("bundleId")),
    "app-store-connect_add-beta-tester-to-group": lambda args: api.add_beta_tester_to_group(
        email=args.get("email"),
        group_id=args.get("groupId")),
    "app-store-connect_release-version": lambda args: api.release_version(
        bundle_id=args.get("bundleId"),
        version_string=args.get("version"),
        build_number=args.get("buildNumber"),
        platform=args.get("platform", "IOS")),
    "app-store-connect_get-performance-metrics": lambda args: api.get_performance_metrics(
        bundle_id=args.get("bundleId")),
}


def handle_tools_call(message):
    """Handle the tools/call message from Cursor."""
    params = message.get("params", {})
    tool_name = params.get("name")
    args = params.get("arguments", {})

    logging.info(
        "Handling tool call for tool '%s' with args: %s", tool_name, args)

    result = None
    error = None

    handler = TOOL_DISPATCH.get(tool_name)
    if handler is None:
        error = {
            "code": -32601,
            "message": f"Tool '{tool_name}' not found"
        }
    else:
        try:
            result = handler(args)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error(
                "Error calling tool %s: %s", tool_name, e, exc_info=True)
            error = {
                "code": -32600,
                "message": f"Error executing tool '{tool_name}': {e}"
            }

    response = {
        "jsonrpc": "2.0",
        "id": message.get("id"),
    }
    if error:
        response["error"] = error
    else:
        # The client expects the result to have a "content" key with an array of content blocks.
        # We will format the JSON result as a string inside a "text" content
        # block.
        response["result"] = {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }

    return response


def handle_notification(message):  # pylint: disable=unused-argument
    """Handle notification messages from Cursor."""
    # Notifications don't require a response
    return None


def read_message():
    """Read a JSON message from stdin.

    Returns:
        dict or None: Parsed JSON message or None if error/EOF.
    """
    try:
        # Read a line from stdin
        line = sys.stdin.readline()
        if not line:
            logging.info("No input received")
            return None

        logging.info("Raw input received: %s", repr(line))
        return json.loads(line.strip())

    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Error reading message: %s", str(e), exc_info=True)
        return None


def write_message(message):
    """Write a JSON message to stdout.

    Args:
        message (dict): The message to send.
    """
    try:
        # Convert message to JSON string
        json_str = json.dumps(message)
        sys.stdout.write(json_str + "\n")
        sys.stdout.flush()
        logging.info("Sent message: %s", repr(json_str))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Error writing message: %s", str(e), exc_info=True)


def main():
    """Main server loop for handling MCP messages."""
    # Log basic environment info
    logging.info("=== Environment Information ===")
    logging.info("Python version: %s", sys.version)
    logging.info("Python executable: %s", sys.executable)
    logging.info("Current working directory: %s", os.getcwd())
    logging.info("PYTHONPATH: %s", os.environ.get('PYTHONPATH', 'Not set'))
    logging.info("PATH: %s", os.environ.get('PATH', 'Not set'))

    # Keep the connection alive and handle messages
    logging.info("=== Starting message loop ===")
    while True:
        try:
            # Read a message
            logging.info("Waiting for input...")
            message = read_message()

            if message:
                method = message.get("method", "")
                logging.info("Received method: %s", method)

                response = None
                # Handle the message based on its method
                if method == "initialize":
                    response = handle_initialize(message)
                elif method == "tools/list":
                    response = handle_tools_list(message)
                elif method == "tools/call":
                    response = handle_tools_call(message)
                elif method and method.startswith("notifications/"):
                    handle_notification(message)
                elif "id" in message:  # Only respond to requests, not notifications
                    response = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Method '{method}' not found"
                        }
                    }

                if response:
                    write_message(response)
            else:
                logging.warning("No valid message received, exiting loop.")
                break

        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error(
                "Error during message handling: %s", str(e),
                exc_info=True)
            # Try to send an error response if possible
            if 'message' in locals() and message and 'id' in message:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32000,
                        "message": f"Internal server error: {e}"
                    }
                }
                write_message(error_response)
            break

    logging.info("=== Message loop ended ===")


if __name__ == "__main__":
    main()
