import subprocess
import os
import threading
import base64

class BashInterface:
    def __init__(self, base_path):
        self.base_path = base_path
        self.client_process = None
        self.output_thread = None
        self.callback = None

    def start_client(self, callback):
        self.callback = callback
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
        def listen():
            for line in self.client_process.stdout:
                if self.callback:
                    self.callback(line.strip())

        self.output_thread = threading.Thread(target=listen, daemon=True)
        self.output_thread.start()

    def send_command(self, cmd):
        if self.client_process and self.client_process.stdin:
            self.client_process.stdin.write(cmd + "\n")
            self.client_process.stdin.flush()

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
