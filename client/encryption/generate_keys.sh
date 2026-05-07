#!/bin/bash
# generate_keys.sh - RSA 4096-bit key pair generation

KEY_DIR="../keys"
mkdir -p "$KEY_DIR"

if [ -f "$KEY_DIR/private.pem" ]; then
    echo "Keys already exist. Skipping generation."
    exit 0
fi

echo "Generating RSA 4096-bit private key..."
openssl genpkey -algorithm RSA -out "$KEY_DIR/private.pem" -pkeyopt rsa_keygen_bits:4096

echo "Extracting public key..."
openssl rsa -pubout -in "$KEY_DIR/private.pem" -out "$KEY_DIR/public.pem"

chmod 600 "$KEY_DIR/private.pem"
echo "Keys generated in $KEY_DIR"
