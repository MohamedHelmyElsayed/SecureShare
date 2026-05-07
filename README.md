# Secure E2EE Chat & File Sharing System

A production-grade, end-to-end encrypted messaging platform featuring a Bash-powered backend and a modern PyQt5 GUI.

## Features
- **Real-Time Messaging**: Instant delivery via socket communication.
- **End-to-End Encryption**: RSA-4096 for key exchange, AES-256-CBC for payloads.
- **Secure File Sharing**: Encrypted binary transfers.
- **Multi-User Support**: Concurrent connections handled via `socat` forks.
- **Modern UI**: Dark-themed, Discord-inspired interface.

## Tech Stack
- **Backend**: Bash, `socat`, `openssl`
- **Frontend**: Python 3, PyQt5
- **Security**: Hybrid RSA/AES Encryption

## Installation
1. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## Usage
1. **Start the Server**:
   ```bash
   cd server
   ./server.sh
   ```
2. **Start the GUI**:
   ```bash
   python3 gui/main.py
   ```

## Architecture
The system uses a unique hybrid architecture:
- **Bash Client Core**: Handles raw socket communication and file system operations.
- **Python GUI**: Interfaces with the Bash core via subprocess pipes, maintaining a clean separation between UI logic and security protocols.
- **Encryption Layer**: Implemented as standalone Bash modules to ensure portability and ease of audit.

## Security Explanation
- **Private Keys**: Generated and stored locally on the client machine. Never sent to the server.
- **Public Keys**: Exchanged through the server upon starting a chat session.
- **Server Privacy**: The server acts only as a router. Since messages are encrypted with the recipient's public key before leaving the sender's machine, the server can never decrypt or inspect the content.
