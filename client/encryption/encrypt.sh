#!/bin/bash
# encrypt.sh - Hybrid Encryption (AES-256-CBC + RSA-4096)
# Usage: ./encrypt.sh <recipient_pub_key> <input_file> <output_file>

PUB_KEY=$1
INPUT=$2
OUTPUT=$3

if [ ! -f "$PUB_KEY" ] || [ ! -f "$INPUT" ]; then
    echo "Usage: ./encrypt.sh <recipient_pub_key> <input_file> <output_file>"
    exit 1
fi

TEMP_DIR="../temp"
mkdir -p "$TEMP_DIR"
AES_KEY_FILE="$TEMP_DIR/aes.key"
ENC_AES_KEY_FILE="$TEMP_DIR/aes.key.enc"
ENC_DATA_FILE="$TEMP_DIR/data.enc"

# 1. Generate random AES-256 key (32 bytes)
openssl rand -hex 32 > "$AES_KEY_FILE"
AES_KEY=$(cat "$AES_KEY_FILE")

# 2. Encrypt data with AES
openssl enc -aes-256-cbc -salt -in "$INPUT" -out "$ENC_DATA_FILE" -pass pass:"$AES_KEY" -pbkdf2

# 3. Encrypt AES key with RSA Public Key
openssl pkeyutl -encrypt -pubin -inkey "$PUB_KEY" -in "$AES_KEY_FILE" -out "$ENC_AES_KEY_FILE"

# 4. Combine: Encrypted AES Key (fixed 512 bytes for RSA-4096) + Encrypted Data
cat "$ENC_AES_KEY_FILE" "$ENC_DATA_FILE" > "$OUTPUT"

# Cleanup
rm -f "$AES_KEY_FILE" "$ENC_AES_KEY_FILE" "$ENC_DATA_FILE"

echo "Encryption complete: $OUTPUT"
