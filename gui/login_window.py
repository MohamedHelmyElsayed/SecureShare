import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoginWindow(QWidget):
    switch_to_register = pyqtSignal()
    login_success = pyqtSignal(str)

    def __init__(self, bash):
        super().__init__()
        self.bash = bash
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Secure Chat - Login")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Welcome Back")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Login to your secure account")
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

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Create an account")
        self.register_btn.setObjectName("IconButton")
        self.register_btn.clicked.connect(self.switch_to_register.emit)
        layout.addWidget(self.register_btn)

        layout.addStretch()
        self.setLayout(layout)

    def handle_login(self):
        user = self.username.text()
        pw = self.password.text()
        if not user or not pw:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        # Simple hash simulation for demo, real implementation should use a better hash
        import hashlib
        pw_hash = hashlib.sha256(pw.encode()).hexdigest()
        
        self.bash.send_command(f"LOGIN|{user}|{pw_hash}")

    def on_server_response(self, response):
        if response.startswith("OK|Login successful"):
            self.login_success.emit(self.username.text())
        elif response.startswith("ERR|"):
            QMessageBox.critical(self, "Login Failed", response.split("|")[1])
