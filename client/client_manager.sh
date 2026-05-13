#!/bin/bash
# client_manager.sh - Unified interface for SecureShare
# This script orchestrates encryption and communication.

BASE_DIR=$(cd "$(dirname "$0")" && pwd)
CLIENT_SH="$BASE_DIR/client.sh"
ENC_SH="$BASE_DIR/encryption/encrypt.sh"
DEC_SH="$BASE_DIR/encryption/decrypt.sh"
KEY_GEN_SH="$BASE_DIR/encryption/generate_keys.sh"
TEMP_DIR="$BASE_DIR/temp"
KEYS_DIR="$BASE_DIR/keys"
DOWNLOADS_DIR="$BASE_DIR/downloads"

mkdir -p "$TEMP_DIR" "$DOWNLOADS_DIR"

log_info() { echo -e "\e[32m[INFO]\e[0m $1"; }
log_err() { echo -e "\e[31m[ERROR]\e[0m $1"; }

# Function to send a command and wait for response
# Uses a background process to read from the socket
send_cmd() {
    local cmd="$1"
    # This is a simplified version. In a real app, we'd use a background socat.
    # For this CLI tool, we'll use a temporary pipe.
    local response=$(echo "$cmd" | "$CLIENT_SH" 2>/dev/null | head -n 1)
    echo "$response"
}

case "$1" in
    "init")
        bash "$KEY_GEN_SH"
        ;;
        
    "register")
        username=$2
        password=$3
        [ -z "$username" ] || [ -z "$password" ] && { echo "Usage: $0 register <user> <pass>"; exit 1; }
        
        pass_hash=$(echo -n "$password" | sha256sum | cut -d' ' -f1)
        pub_key=$(cat "$KEYS_DIR/public.pem" | base64 -w 0)
        
        resp=$(send_cmd "REG|$username|$pass_hash|$pub_key")
        echo "$resp"
        ;;
        
    "login")
        username=$2
        password=$3
        [ -z "$username" ] || [ -z "$password" ] && { echo "Usage: $0 login <user> <pass>"; exit 1; }
        
        pass_hash=$(echo -n "$password" | sha256sum | cut -d' ' -f1)
        resp=$(send_cmd "LOGIN|$username|$pass_hash")
        echo "$resp"
        ;;

    "send")
        # $0 send <recipient> <message>
        recipient=$2
        message=$3
        [ -z "$recipient" ] || [ -z "$message" ] && { echo "Usage: $0 send <recipient> <msg>"; exit 1; }
        
        log_info "Fetching public key for $recipient..."
        resp=$(send_cmd "GET_KEY|$recipient")
        if [[ $resp == SYS|KEY|* ]]; then
            pub_key_b64=$(echo "$resp" | cut -d'|' -f4)
            echo "$pub_key_b64" | base64 -d > "$TEMP_DIR/peer_pub.pem"
            
            echo "$message" > "$TEMP_DIR/msg.txt"
            bash "$ENC_SH" "$TEMP_DIR/peer_pub.pem" "$TEMP_DIR/msg.txt" "$TEMP_DIR/msg.enc" >/dev/null
            
            enc_data=$(cat "$TEMP_DIR/msg.enc" | base64 -w 0)
            echo "MSG|$(whoami)|$recipient|$enc_data"
            
            # Local Logging
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] TO $recipient: $message" >> "$BASE_DIR/chat.log"
        else
            log_err "Could not find user $recipient"
        fi
        ;;

    "send_file")
        # $0 send_file <recipient> <file_path>
        recipient=$2
        file_path=$3
        [ -z "$recipient" ] || [ ! -f "$file_path" ] && { echo "Usage: $0 send_file <recipient> <path>"; exit 1; }
        
        log_info "Encrypting file $file_path for $recipient..."
        resp=$(send_cmd "GET_KEY|$recipient")
        if [[ $resp == SYS|KEY|* ]]; then
            pub_key_b64=$(echo "$resp" | cut -d'|' -f4)
            echo "$pub_key_b64" | base64 -d > "$TEMP_DIR/peer_pub.pem"
            
            bash "$ENC_SH" "$TEMP_DIR/peer_pub.pem" "$file_path" "$TEMP_DIR/file.enc" >/dev/null
            enc_data=$(cat "$TEMP_DIR/file.enc" | base64 -w 0)
            
            filename=$(basename "$file_path")
            echo "FILE|$(whoami)|$recipient|$filename:$enc_data"
            log_info "File sent successfully."
        else
            log_err "Could not find user $recipient"
        fi
        ;;

    *)
        echo "Usage: $0 {init|register|login|send|send_file}"
        exit 1
        ;;
esac
