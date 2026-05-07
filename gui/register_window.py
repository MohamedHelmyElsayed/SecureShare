import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import hashlib
import base64

class RegisterWindow(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self, bash):
        super().__init__()
        self.bash = bash
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Secure Chat - Register")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Join Secure Chat")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Create your end-to-end encrypted account")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)

        self.login_btn = QPushButton("Already have an account? Login")
        self.login_btn.setObjectName("IconButton")
        self.login_btn.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(self.login_btn)

        layout.addStretch()
        self.setLayout(layout)

    def handle_register(self):
        user = self.username.text()
        pw = self.password.text()
        if not user or not pw:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        # 1. Generate RSA Keys
        self.bash.generate_keys()
        
        # 2. Read public key
        pub_key_path = os.path.join(self.bash.base_path, "client", "keys", "public.pem")
        with open(pub_key_path, "rb") as f:
            pub_key_b64 = base64.b64encode(f.read()).decode()

        # 3. Hash password
        pw_hash = hashlib.sha256(pw.encode()).hexdigest()
        
        # 4. Send REG command
        self.bash.send_command(f"REG|{user}|{pw_hash}|{pub_key_b64}")

    def on_server_response(self, response):
        if response.startswith("OK|Registration successful"):
            QMessageBox.information(self, "Success", "Registration successful! You can now login.")
            self.switch_to_login.emit()
        elif response.startswith("ERR|"):
            QMessageBox.critical(self, "Registration Failed", response.split("|")[1])
