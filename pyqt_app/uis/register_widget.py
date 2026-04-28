from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtSvgWidgets import QSvgWidget

import requests
import json
import base64

from uis.emails_widget import EmailsWidget
from uis.compiled.register import Ui_Form


def bytes_to_base64(bytes) -> str:
    return base64.b64encode(bytes).decode()


class RegisterWidget(QWidget, Ui_Form):
    def __init__(self, welcome_screen):
        super().__init__()
        self.welcome_screen = welcome_screen
        self.url: str | None = None
        self.pfp = None
        self.setupUi(self)
        self.setWindowTitle("Register")
        self.setupUI()

    def setupUI(self):
        self.svg_widget = QSvgWidget("assets/logo.svg")
        self.svg_widget.setGeometry(50, 50, 200, 200)
        self.svg_widget.setMinimumSize(32, 32)
        self.svg_widget.setMaximumSize(64, 64)
        self.imgLayout.insertWidget(1, self.svg_widget)

        self.register_button.clicked.connect(self.attempt_register)
        self.back_button.clicked.connect(self.go_back)
        self.open_button.clicked.connect(self.get_image)

    def do_error(self, content, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(content)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def get_image(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        try:
            with open(fname, "rb") as f:
                self.pfp = bytes_to_base64(f.read())
        except Exception:
            return

    def attempt_register(self, event):
        username = self.username_edit.text()
        displayname = self.displayname_edit.text()
        password = self.password_edit.text()
        password_again =  self.password_again_edit.text()
        if not username.strip() or not password.strip() or not displayname.strip():
            self.do_error("Missing password or username", "Error")
            return
        if password != password_again:
            self.do_error("Passwords do not match", "Error")
            return

        with open("config.json", "r") as file:
            data = json.load(file)
        url = data["server_url"]

        try:
            if self.pfp:
                request = requests.post(url + "api/users", json={"username": username,
                                                                 "displayname": displayname,
                                                                 "password": password,
                                                                 "pfp": self.pfp})
            else:
                request = requests.post(url + "api/users", json={"username": username,
                                                                 "displayname": displayname,
                                                                 "password": password})
        except Exception as e:
            msg = QMessageBox()
            msg.setText(str(e))
            retval = msg.exec()
            return

        if request.status_code != 200:
            msg = QMessageBox()
            msg.setText("Username already in use")
            retval = msg.exec()
            return

        request = requests.post(url + "api/login", json={"username": username, "password": password})

        if (error := request.status_code) != 200:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"Login failed, error {error}")
            msg.setWindowTitle("Error")
            retval = msg.exec()
            return

        with open("do_not_share.json", "r") as file:
            data = json.load(file)
        data["sc"] = request.cookies.get_dict()["session"]
        with open("do_not_share.json", "w") as file:
            json.dump(data, file)

        self.welcome_screen.open_mail()
        self.close()

    def go_back(self):
        self.welcome_screen.show()
        self.close()