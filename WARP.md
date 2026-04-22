# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an App Store Connect MCP (Model Context Protocol) server that exposes Apple's App Store Connect API functionality for use with AI assistants. It implements the JSON-RPC protocol to provide tools for managing iOS apps, builds, beta testing, and submissions.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Configuration setup (required before first use)
# Copy .env.example to .env and fill in your App Store Connect API credentials
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=appstore_service --cov=app_store_connect_api

# Run specific test file with verbose output
pytest tests/test_app_store_connect_api.py -v

# Run only fast tests (exclude slow/integration tests)
pytest -m "not slow"

# Run single test method
pytest tests/test_app_store_connect_api.py::TestAppStoreConnectApi::test_list_apps -v
```

### Server Operations
```bash
# Start the MCP server (production)
./start_app_store_connect_server.sh

# Test MCP tool discovery
python check_tools.py

# Start server directly (development)
python app_store_connect_server.py
```

### Logs and Debugging
```bash
# View server logs
tail -f logs/app_store_connect_server.log

# Check startup logs
tail -f logs/app_store_connect_startup.log
```

## Architecture Overview

### Core Components

**MCP Server Layer (`app_store_connect_server.py`)**
- Implements JSON-RPC 2.0 protocol for MCP communication
- Handles initialize, tools/list, and tools/call requests
- Exposes 10 primary tools for App Store Connect operations
- Manages logging and error handling for the protocol layer

**API Facade (`app_store_connect_api.py`)**  
- Thin wrapper providing clean function interfaces
- Handles parameter validation and error formatting
- Bridges between MCP server and service layer
- Single point of entry for all business operations

**Service Architecture (`appstore_service/`)**
- **`app_store.py`**: Main orchestrator class that coordinates all operations
- **`api_auth.py`**: JWT authentication handling for App Store Connect API
- **Service modules**: Domain-specific services for different API areas
  - `app_info_service.py`: App metadata and information
  - `build_service.py`: Build management and retrieval
  - `beta_service.py`: TestFlight and beta testing operations
  - `version_service.py`: App version and release management
  - `performance_service.py`: App performance metrics
- **`utils.py`**: Shared utility functions across services

### Data Flow Architecture

1. **MCP Client** (AI Assistant) → JSON-RPC request
2. **MCP Server** → parses request, validates tool/parameters
3. **API Facade** → routes to appropriate function, validates business parameters  
4. **AppStore Orchestrator** → coordinates service calls, handles app ID resolution
5. **Domain Services** → make authenticated API calls to Apple's servers
6. **Auth Service** → generates/manages JWT tokens for each request

### Key Architectural Patterns

**Bundle ID to App ID Resolution**: Most operations require internal Apple app IDs, but users work with bundle IDs. The `AppStore` class automatically resolves bundle IDs to app IDs using `app_info_service.get_app_id_by_bundle_id()`.

**Centralized Error Handling**: All HTTP errors are caught and normalized by `AppStore._handle_error()` to return consistent JSON error responses.

**Service Composition**: The `AppStore` class composes multiple domain services, each handling a specific area of functionality while sharing the same authentication instance.

**JWT Token Management**: Authentication tokens are generated on-demand with 19-minute expiration (just below Apple's 20-minute maximum) and include proper headers for API authentication.

## Configuration Requirements

Credentials are loaded from a `.env` file at the project root via `python-dotenv` (see `.env.example` for the template):
- `ASC_KEY_ID`: 10-character key ID from App Store Connect
- `ASC_ISSUER_ID`: UUID issuer ID from App Store Connect
- `ASC_PRIVATE_KEY_PATH`: Path to your downloaded .p8 private key file (defaults to `AppStoreConnectAuthKey.p8`)
- `ASC_APP_ID`: Optional default app ID for operations
- `ASC_EXPIRATION_MINUTES`: JWT expiration in minutes (defaults to 19; Apple's maximum is 20)

## Testing Architecture

Tests use pytest with comprehensive mocking to avoid actual API calls:
- **Unit tests**: Focus on parameter validation and business logic
- **Mock-based**: All external API calls are mocked using `unittest.mock`
- **Fast execution**: Tests run quickly without network dependencies
- **Coverage tracking**: Uses pytest-cov for coverage reporting
- **Test markers**: `slow` and `integration` markers for test categorization

## MCP Tool Interface

The server exposes these standardized tools (all prefixed `app-store-connect_`):
- `app-store-connect_list-apps`: Get all applications
- `app-store-connect_get-app-info`: Get detailed app information
- `app-store-connect_list-builds`: Get builds for an app
- `app-store-connect_list-beta-groups`: Get beta groups for an app
- `app-store-connect_list-testers-in-group`: Get testers in a beta group
- `app-store-connect_create-beta-group`: Create a new beta group
- `app-store-connect_submit-for-review`: Submit an app version for review
- `app-store-connect_add-beta-tester-to-group`: Add a beta tester to a group
- `app-store-connect_release-version`: Release a new app version
- `app-store-connect_get-performance-metrics`: Get performance metrics for an app

Each tool includes JSON schema validation for input parameters and returns structured JSON responses.
