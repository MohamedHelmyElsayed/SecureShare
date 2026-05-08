#!/bin/bash
# handle_client.sh - Logic for handling individual client connections

BASE_DIR=$(pwd)
USERS_DB="$BASE_DIR/users.db"
ONLINE_USERS="$BASE_DIR/online_users.txt"
PIPE_DIR="$BASE_DIR/pipes"
mkdir -p "$PIPE_DIR"

CURRENT_USER=""

# Function to log activity
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$BASE_DIR/logs/server.log"
}

# Cleanup on exit
cleanup() {
    if [ -n "$CURRENT_USER" ]; then
        sed -i "/^$CURRENT_USER$/d" "$ONLINE_USERS"
        rm -f "$PIPE_DIR/$CURRENT_USER"
        log "User $CURRENT_USER disconnected."
    fi
    exit
}
trap cleanup EXIT

# Protocol loop
while read -r line; do
    # Remove trailing carriage return if present (Windows clients)
    line="${line%$'\r'}"
    
    IFS='|' read -r CMD SENDER RECEIVER DATA <<< "$line"
    
    case "$CMD" in
        "REG")
            # REG|username|password_hash|pub_key
            if grep -q "^$SENDER|" "$USERS_DB"; then
                echo "ERR|User already exists"
            else
                printf "%s|%s|%s\n" "$SENDER" "$RECEIVER" "$DATA" >> "$USERS_DB"
                echo "OK|Registration successful"
                log "User $SENDER registered."
            fi
            ;;
            
        "LOGIN")
            # LOGIN|username|password_hash
            USER_ENTRY=$(grep "^$SENDER|" "$USERS_DB")
            if [ -n "$USER_ENTRY" ]; then
                STORED_HASH=$(echo "$USER_ENTRY" | cut -d'|' -f2)
                if [ "$RECEIVER" == "$STORED_HASH" ]; then
                    CURRENT_USER="$SENDER"
                    echo "$SENDER" >> "$ONLINE_USERS"
                    # Create a pipe for this user to receive messages
                    mkfifo "$PIPE_DIR/$SENDER"
                    echo "OK|Login successful"
                    log "User $SENDER logged in."
                    
                    # Start a background process to forward messages from pipe to socket
                    (
                        while [ -p "$PIPE_DIR/$SENDER" ]; do
                            if read -r msg < "$PIPE_DIR/$SENDER"; then
                                printf "%s\n" "$msg"
                            fi
                        done
                    ) &
                else
                    echo "ERR|Invalid password"
                fi
            else
                echo "ERR|User not found"
            fi
            ;;
            
        "GET_USERS")
            USERS=$(paste -sd "," "$ONLINE_USERS")
            echo "SYS|ONLINE_USERS|$USERS"
            ;;
            
        "GET_KEY")
            # GET_KEY|target_user
            USER_ENTRY=$(grep "^$SENDER|" "$USERS_DB")
            if [ -n "$USER_ENTRY" ]; then
                PUB_KEY=$(echo "$USER_ENTRY" | cut -d'|' -f3)
                printf "SYS|KEY|%s|%s\n" "$SENDER" "$PUB_KEY"
            else
                echo "ERR|User not found"
            fi
            ;;
            
        "MSG"|"FILE"|"MSG_CHUNK"|"FILE_CHUNK")
            # CMD|sender|receiver|data
            if [ -p "$PIPE_DIR/$RECEIVER" ]; then
                printf "%s|%s|%s|%s\n" "$CMD" "$SENDER" "$RECEIVER" "$DATA" > "$PIPE_DIR/$RECEIVER"
                log "$CMD from $SENDER to $RECEIVER"
            else
                echo "ERR|User $RECEIVER is offline"
            fi
            ;;
            
        "EXIT")
            cleanup
            ;;
            
        *)
            echo "ERR|Unknown command"
            ;;
    esac
done
