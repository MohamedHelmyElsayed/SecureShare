from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os

class MessageBubble(QWidget):
    def __init__(self, text, sender, is_own=False):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(400)
        
        if is_own:
            self.label.setObjectName("OwnMessageText")
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            self.label.setObjectName("MessageText")
            sender_label = QLabel(f"<b>{sender}</b>")
            sender_label.setStyleSheet("color: #89b4fa; font-size: 10px;")
            
            v_layout = QVBoxLayout()
            v_layout.addWidget(sender_label)
            v_layout.addWidget(self.label)
            
            layout.addLayout(v_layout)
            layout.addStretch()
            
        self.setLayout(layout)

class ChatWindow(QMainWindow):
    def __init__(self, bash, username):
        super().__init__()
        self.bash = bash
        self.username = username
        self.current_recipient = None
        self.keys_cache = {} # username -> pub_key_path
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Secure Chat - {self.username}")
        self.setMinimumSize(900, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("UserList")
        self.sidebar.setFixedWidth(250)
        self.sidebar.itemClicked.connect(self.select_user)
        main_layout.addWidget(self.sidebar)

        # Chat Area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        
        # Header
        self.header = QLabel("Select a contact to start chatting")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px; border-bottom: 1px solid #313244;")
        chat_layout.addWidget(self.header)

        # Messages
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.addStretch()
        self.scroll.setWidget(self.message_container)
        chat_layout.addWidget(self.scroll)

        # Input
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedWidth(40)
        self.attach_btn.clicked.connect(self.send_file)
        input_layout.addWidget(self.attach_btn)

        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Type a secure message...")
        self.msg_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.msg_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        chat_layout.addLayout(input_layout)
        main_layout.addWidget(chat_container)

        # Start timer to refresh user list
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_users)
        self.timer.start(5000)
        self.refresh_users()

    def refresh_users(self):
        self.bash.send_command("GET_USERS")

    def select_user(self, item):
        self.current_recipient = item.text()
        self.header.setText(f"Chatting with {self.current_recipient} (E2EE Active)")
        # Request key if not in cache
        if self.current_recipient not in self.keys_cache:
            self.bash.send_command(f"GET_KEY|{self.current_recipient}")

    def send_message(self):
        msg = self.msg_input.text()
        if not msg or not self.current_recipient:
            return

        if self.current_recipient not in self.keys_cache:
            QMessageBox.warning(self, "Error", "Waiting for recipient's public key...")
            return

        # 1. Encrypt message
        pub_key_path = self.keys_cache[self.current_recipient]
        encrypted_data = self.bash.encrypt_message(pub_key_path, msg)
        
        # 2. Send command
        self.bash.send_command(f"MSG|{self.username}|{self.current_recipient}|{encrypted_data}")
        
        # 3. Update UI
        self.add_message(msg, self.username, is_own=True)
        self.msg_input.clear()

    def send_file(self):
        if not self.current_recipient:
            QMessageBox.warning(self, "Error", "Select a contact first")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Send")
        if not file_path:
            return
            
        filename = os.path.basename(file_path)
        
        if self.current_recipient not in self.keys_cache:
            QMessageBox.warning(self, "Error", "Waiting for recipient's public key...")
            return

        # 1. Encrypt file
        pub_key_path = self.keys_cache[self.current_recipient]
        temp_out = os.path.join(self.bash.base_path, "client", "temp", "file_out.enc")
        
        import subprocess
        import base64
        script = os.path.join(self.bash.base_path, "client", "encryption", "encrypt.sh")
        subprocess.run(["bash", script, pub_key_path, file_path, temp_out], 
                       cwd=os.path.join(self.bash.base_path, "client", "encryption"))
        
        with open(temp_out, "rb") as f:
            encrypted_data = base64.b64encode(f.read()).decode()
            
        # 2. Send command
        self.bash.send_command(f"FILE|{self.username}|{self.current_recipient}|{filename}|{encrypted_data}")
        
        # 3. Update UI
        self.add_message(f"📁 Sent file: {filename}", self.username, is_own=True)

    def add_message(self, text, sender, is_own=False):
        bubble = MessageBubble(text, sender, is_own)
        # Add before the stretch
        self.message_layout.insertWidget(self.message_layout.count() - 1, bubble)
        # Scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def on_server_response(self, response):
        parts = response.split("|")
        if parts[0] == "SYS":
            if parts[1] == "ONLINE_USERS":
                users = parts[2].split(",")
                self.sidebar.clear()
                for u in users:
                    if u and u != self.username:
                        self.sidebar.addItem(u)
            elif parts[1] == "KEY":
                # SYS|KEY|user|pub_key_b64
                user = parts[2]
                key_data = parts[3]
                key_path = os.path.join(self.bash.base_path, "client", "temp", f"{user}_pub.pem")
                import base64
                with open(key_path, "wb") as f:
                    f.write(base64.b64decode(key_data))
                self.keys_cache[user] = key_path

        elif parts[0] == "MSG":
            # MSG|sender|receiver|data
            sender = parts[1]
            enc_data = parts[3]
            # Decrypt
            priv_key_path = os.path.join(self.bash.base_path, "client", "keys", "private.pem")
            decrypted_msg = self.bash.decrypt_message(priv_key_path, enc_data)
            self.add_message(decrypted_msg, sender)

        elif parts[0] == "FILE":
            # FILE|sender|receiver|filename|data
            sender = parts[1]
            filename = parts[3]
            enc_data = parts[4]
            
            # Decrypt
            priv_key_path = os.path.join(self.bash.base_path, "client", "keys", "private.pem")
            save_path = os.path.join(self.bash.base_path, "client", "downloads", filename)
            
            # Use temp file for decryption
            temp_in = os.path.join(self.bash.base_path, "client", "temp", "file_in.enc")
            import base64
            with open(temp_in, "wb") as f:
                f.write(base64.b64decode(enc_data))
                
            import subprocess
            script = os.path.join(self.bash.base_path, "client", "encryption", "decrypt.sh")
            subprocess.run(["bash", script, priv_key_path, temp_in, save_path],
                           cwd=os.path.join(self.bash.base_path, "client", "encryption"))
            
            self.add_message(f"📁 Received file: {filename} (Saved to downloads)", sender)
