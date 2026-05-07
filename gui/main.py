import sys
import os
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import pyqtSignal, QObject
from login_window import LoginWindow
from register_window import RegisterWindow
from chat_window import ChatWindow
from utils.bash_interface import BashInterface

class AppController(QObject):
    def __init__(self):
        super().__init__()
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.bash = BashInterface(self.base_path)
        
        self.stack = QStackedWidget()
        self.login_win = LoginWindow(self.bash)
        self.register_win = RegisterWindow(self.bash)
        
        self.stack.addWidget(self.login_win)
        self.stack.addWidget(self.register_win)
        
        self.login_win.switch_to_register.connect(lambda: self.stack.setCurrentWidget(self.register_win))
        self.register_win.switch_to_login.connect(lambda: self.stack.setCurrentWidget(self.login_win))
        self.login_win.login_success.connect(self.start_chat)

        # Start Bash Client
        self.bash.output_received.connect(self.handle_bash_output)
        self.bash.start_client()

        self.stack.show()

    def handle_bash_output(self, line):
        # Route output to current active window
        current = self.stack.currentWidget()
        if hasattr(current, "on_server_response"):
            current.on_server_response(line)

    def start_chat(self, username):
        self.chat_win = ChatWindow(self.bash, username)
        self.stack.addWidget(self.chat_win)
        self.stack.setCurrentWidget(self.chat_win)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), "themes", "dark.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
            
    controller = AppController()
    sys.exit(app.exec_())
