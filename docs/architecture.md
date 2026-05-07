# System Architecture

The "Secure Real-Time Chat" system is designed with a modular architecture that separates the presentation layer from the security and networking core.

## Components

### 1. The Server (Bash)
- **Engine**: `socat` TCP-LISTEN.
- **Concurrency**: Process-based (forking).
- **State Management**:
    - `users.db`: Persistent user registry and public keys.
    - `online_users.txt`: Volatile list of current sessions.
    - `pipes/`: Named pipes for inter-process message routing.

### 2. The Client Backend (Bash)
- **Networking**: `client.sh` bridges local stdin/stdout to the remote server.
- **Security**: Modular scripts in `client/encryption/` handle all cryptographic tasks using OpenSSL.

### 3. The GUI (Python/PyQt5)
- **Controller**: `main.py` manages the application lifecycle.
- **Interface**: Modern widgets with QSS styling.
- **IPC**: Uses `subprocess.Popen` with non-blocking pipes to communicate with `client.sh`.

## Data Flow

1. **User Action**: User types a message in the Python GUI.
2. **Encryption**: GUI calls `encrypt.sh` (Bash) to produce an encrypted blob.
3. **Transmission**: GUI writes the `MSG|...` command to the stdin of the `client.sh` subprocess.
4. **Routing**: The Server receives the command, identifies the recipient, and writes the blob to the recipient's named pipe.
5. **Reception**: The recipient's `handle_client.sh` reads from the pipe and sends it over the socket.
6. **Decryption**: Recipient's GUI reads from `client.sh` stdout, calls `decrypt.sh`, and displays the message.
