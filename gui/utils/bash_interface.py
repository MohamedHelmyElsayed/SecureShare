from PyQt5.QtCore import QObject, pyqtSignal
import subprocess
import os
import threading
import base64

class BashInterface(QObject):
    output_received = pyqtSignal(str)

    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path
        self.client_process = None
        self.output_thread = None

    def start_client(self):
        client_sh = os.path.join(self.base_path, "client", "client.sh")
        
        # Start the client.sh as a subprocess
        self.client_process = subprocess.Popen(
            ["bash", client_sh],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Thread to read output from client.sh
        def listen_stdout():
            try:
                for line in self.client_process.stdout:
                    msg = line.strip()
                    if msg:
                        self.output_received.emit(msg)
            except Exception as e:
                print(f"Stdout listener error: {e}")

        # Thread to read errors from client.sh
        def listen_stderr():
            try:
                for line in self.client_process.stderr:
                    err = line.strip()
                    if err:
                        print(f"[BASH ERROR] {err}")
                        if "connection refused" in err.lower():
                            self.output_received.emit("ERR|Connection refused. Is the server running?")
            except Exception as e:
                print(f"Stderr listener error: {e}")

        threading.Thread(target=listen_stdout, daemon=True).start()
        threading.Thread(target=listen_stderr, daemon=True).start()

    def send_command(self, cmd):
        if self.client_process and self.client_process.poll() is None:
            try:
                self.client_process.stdin.write(cmd + "\n")
                self.client_process.stdin.flush()
            except BrokenPipeError:
                print("Error: Connection to backend lost (Broken Pipe)")
                self.output_received.emit("ERR|Lost connection to backend server.")
        else:
            self.output_received.emit("ERR|Backend process is not running. Please restart.")

    def generate_keys(self):
        script = os.path.join(self.base_path, "client", "encryption", "generate_keys.sh")
        subprocess.run(["bash", script], cwd=os.path.join(self.base_path, "client", "encryption"))

    def encrypt_message(self, recipient_pub_key_path, message):
        # Create temp message file
        temp_in = os.path.join(self.base_path, "client", "temp", "msg_in.txt")
        temp_out = os.path.join(self.base_path, "client", "temp", "msg_out.enc")
        
        with open(temp_in, "w") as f:
            f.write(message)
            
        script = os.path.join(self.base_path, "client", "encryption", "encrypt.sh")
        subprocess.run(["bash", script, recipient_pub_key_path, temp_in, temp_out], 
                       cwd=os.path.join(self.base_path, "client", "encryption"))
        
        with open(temp_out, "rb") as f:
            encrypted_data = base64.b64encode(f.read()).decode()
            
        return encrypted_data

    def decrypt_message(self, private_key_path, encrypted_base64):
        temp_in = os.path.join(self.base_path, "client", "temp", "msg_in.enc")
        temp_out = os.path.join(self.base_path, "client", "temp", "msg_out.txt")
        
        with open(temp_in, "wb") as f:
            f.write(base64.b64decode(encrypted_base64))
            
        script = os.path.join(self.base_path, "client", "encryption", "decrypt.sh")
        subprocess.run(["bash", script, private_key_path, temp_in, temp_out],
                       cwd=os.path.join(self.base_path, "client", "encryption"))
        
        if os.path.exists(temp_out):
            with open(temp_out, "r") as f:
                return f.read()
        return "[Decryption Failed]"
