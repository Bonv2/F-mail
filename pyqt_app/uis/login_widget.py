from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtSvgWidgets import QSvgWidget

import requests
import json

from uis.emails_widget import EmailsWidget
from uis.compiled.login import Ui_Form


class LoginWidget(QWidget, Ui_Form):
    def __init__(self, welcome_screen):
        super().__init__()
        self.welcome_screen = welcome_screen
        self.url: str | None = None
        self.setupUi(self)
        self.setWindowTitle("Login")
        self.setupUI()

    def setupUI(self):
        self.svg_widget = QSvgWidget("assets/logo.svg")
        self.svg_widget.setGeometry(50, 50, 200, 200)
        self.svg_widget.setMinimumSize(32, 32)
        self.svg_widget.setMaximumSize(64, 64)
        self.imgLayout.insertWidget(1, self.svg_widget)

        self.login_button.clicked.connect(self.attempt_login)
        self.back_button.clicked.connect(self.go_back)

    def attempt_login(self, event):
        username = self.username_edit.text()
        password = self.password_edit.text()
        print(username, password)
        if not username.strip() or not password.strip():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Missing password or username")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            retval = msg.exec()
            return

        with open("config.json", "r") as file:
            data = json.load(file)
        url = data["server_url"]

        try:
            request = requests.post(url + "api/login", json={"username": username, "password": password})
        except Exception as e:
            msg = QMessageBox()
            msg.setText(str(e))
            retval = msg.exec()
            return

        if (error := request.status_code) != 200:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"Login failed, error {error}")
            msg.setWindowTitle("Error")
            retval = msg.exec()
            return

        try:
            with open("do_not_share.json", "r") as file:
                data = json.load(file)
        except Exception:
            data = {}
        data["sc"] = request.cookies.get_dict()["session"]
        with open("do_not_share.json", "w") as file:
            json.dump(data, file)

        self.welcome_screen.open_mail()
        self.close()

    def go_back(self):
        self.welcome_screen.show()
        self.close()