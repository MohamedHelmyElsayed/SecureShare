#!/bin/bash
# server.sh - Main entry point for the secure chat server

PORT=9999
BASE_DIR=$(pwd)
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
# The TCP-LISTEN,fork option handles concurrency
socat TCP-LISTEN:$PORT,reuseaddr,fork EXEC:"./handle_client.sh"
