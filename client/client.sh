#!/bin/bash
# client.sh - Main client networking core

# Default settings
SERVER_IP="127.0.0.1"
SERVER_PORT=9999

# Parse CLI options
while getopts "s:p:h" opt; do
  case $opt in
    s) SERVER_IP=$OPTARG ;;
    p) SERVER_PORT=$OPTARG ;;
    h) echo "Usage: $0 [-s server_ip] [-p port]"; exit 0 ;;
    *) echo "Usage: $0 [-s server_ip] [-p port]"; exit 1 ;;
  esac
done

# We use socat to bridge stdin/stdout to the server socket
# This allows the Python GUI to just write to this script's stdin
# and read from its stdout.
socat STDIO TCP:$SERVER_IP:$SERVER_PORT
