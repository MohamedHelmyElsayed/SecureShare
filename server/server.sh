#!/bin/bash
# server.sh - Main entry point for the secure chat server

# Default settings
PORT=9999
BASE_DIR=$(pwd)

# Parse CLI options
while getopts "p:h" opt; do
  case $opt in
    p) PORT=$OPTARG ;;
    h) echo "Usage: $0 [-p port]"; exit 0 ;;
    *) echo "Usage: $0 [-p port]"; exit 1 ;;
  esac
done

USERS_DB="$BASE_DIR/users.db"
ONLINE_USERS="$BASE_DIR/online_users.txt"
LOG_DIR="$BASE_DIR/logs"

mkdir -p "$LOG_DIR"
touch "$USERS_DB"
touch "$ONLINE_USERS"

# Clear online users on startup
> "$ONLINE_USERS"

echo "------------------------------------------------"
echo " Secure E2EE Chat Server Starting..."
echo " Port: $PORT"
echo "------------------------------------------------"

# Use socat to listen and fork a handler for each client
socat TCP-LISTEN:$PORT,reuseaddr,fork EXEC:"./handle_client.sh"
