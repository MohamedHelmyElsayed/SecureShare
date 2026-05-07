#!/bin/bash
# decrypt.sh - Hybrid Decryption (AES-256-CBC + RSA-4096)
# Usage: ./decrypt.sh <private_key> <input_file> <output_file>

PRIV_KEY=$1
INPUT=$2
OUTPUT=$3

if [ ! -f "$PRIV_KEY" ] || [ ! -f "$INPUT" ]; then
    echo "Usage: ./decrypt.sh <private_key> <input_file> <output_file>"
    exit 1
fi

TEMP_DIR="../temp"
mkdir -p "$TEMP_DIR"
ENC_AES_KEY_FILE="$TEMP_DIR/aes.key.enc"
ENC_DATA_FILE="$TEMP_DIR/data.enc"
AES_KEY_FILE="$TEMP_DIR/aes.key"

# 1. Extract Encrypted AES Key (first 512 bytes for RSA-4096)
dd if="$INPUT" of="$ENC_AES_KEY_FILE" bs=512 count=1 2>/dev/null

# 2. Extract Encrypted Data (the rest)
dd if="$INPUT" of="$ENC_DATA_FILE" bs=512 skip=1 2>/dev/null

# 3. Decrypt AES key with RSA Private Key
openssl pkeyutl -decrypt -inkey "$PRIV_KEY" -in "$ENC_AES_KEY_FILE" -out "$AES_KEY_FILE"

AES_KEY=$(cat "$AES_KEY_FILE")

# 4. Decrypt data with AES
openssl enc -aes-256-cbc -d -in "$ENC_DATA_FILE" -out "$OUTPUT" -pass pass:"$AES_KEY" -pbkdf2

# Cleanup
rm -f "$ENC_AES_KEY_FILE" "$ENC_DATA_FILE" "$AES_KEY_FILE"

echo "Decryption complete: $OUTPUT"
