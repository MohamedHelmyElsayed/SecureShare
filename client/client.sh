#!/bin/bash
# client.sh - Main client networking core

SERVER_IP="127.0.0.1"
SERVER_PORT=9999

# We use socat to bridge stdin/stdout to the server socket
# This allows the Python GUI to just write to this script's stdin
# and read from its stdout.
socat STDIO TCP:$SERVER_IP:$SERVER_PORT
