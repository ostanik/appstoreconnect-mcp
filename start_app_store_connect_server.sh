#!/bin/bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

# --- Logging for setup ---
# We'll create a new log file for each run to keep things clean.
mkdir -p "$(dirname "$0")/logs"
LOG_FILE="$(dirname "$0")/logs/app_store_connect_startup.log"
echo "--- Starting MCP Server at $(date) ---" > "$LOG_FILE"
echo "Current directory: $(pwd)" >> "$LOG_FILE"

# --- pyenv Initialization ---
if command -v pyenv &> /dev/null; then
    echo "Initializing pyenv..." >> "$LOG_FILE"
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    
    # Set the python version
    pyenv shell 3.10.4
    echo "pyenv shell set to 3.10.4" >> "$LOG_FILE"
    echo "which python: $(which python)" >> "$LOG_FILE"
    echo "python version: $(python --version)" >> "$LOG_FILE"
else
    echo "pyenv not found, using system python." >> "$LOG_FILE"
fi

echo "Starting test_env.py..." >> "$LOG_FILE"

# --- Execute the Python Server ---
# The server will use stdout for JSON-RPC communication with Cursor.
# We will redirect the server's stderr to our log file for debugging.
python3 app_store_connect_server.py 2>> "$LOG_FILE"

# This line will run after the python script exits.
echo "--- MCP Server script finished at $(date) ---" >> "$LOG_FILE" 