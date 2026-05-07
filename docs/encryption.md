# Encryption Workflow

This system implements a hybrid encryption scheme to ensure both performance and security.

## 1. Key Generation
Each client generates an RSA-4096 key pair locally using `generate_keys.sh`.
- **Private Key**: Stored in `client/keys/private.pem` (chmod 600).
- **Public Key**: Sent to the server during registration.

## 2. Message Encryption (Sender)
When a user sends a message to a recipient:
1. The client requests the recipient's public key from the server.
2. The client generates a random 256-bit AES key.
3. The message is encrypted using AES-256-CBC with the random key (`openssl enc`).
4. The AES key is encrypted using the recipient's RSA public key (`openssl pkeyutl`).
5. The encrypted AES key (512 bytes) and the encrypted message are concatenated and sent.

## 3. Message Decryption (Receiver)
When a user receives an encrypted packet:
1. The client splits the packet: the first 512 bytes are the encrypted AES key, the rest is the encrypted data.
2. The encrypted AES key is decrypted using the receiver's RSA private key.
3. The encrypted data is decrypted using the recovered AES key.

## File Sharing
File sharing follows the exact same workflow, treating the binary file as the payload for the AES encryption.
