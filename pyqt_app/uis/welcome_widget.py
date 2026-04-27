from PyQt6.QtWidgets import QWidget
from PyQt6.QtSvgWidgets import QSvgWidget
import json
import requests

from uis.login_widget import LoginWidget
from uis.register_widget import RegisterWidget
from uis.emails_widget import EmailsWidget
from uis.compiled.welcome_screen import Ui_Form


class WelcomeWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Welcome")
        self.setupUI()

    def open_mail(self):
        self.email = EmailsWidget(self)
        self.email.show()
        self.close()

    def post_show(self):
        with open("do_not_share.json", "r") as file:
            data = json.load(file)
        try:
            session = data["sc"]
        except KeyError:
            return
        with open("config.json", "r") as file:
            data = json.load(file)
        url = data["server_url"]
        if session:
            ok = requests.get(url + "api/emails", cookies={"session": session})
            if ok.status_code == 200:
                self.open_mail()

    def setupUI(self):
        self.svg_widget = QSvgWidget("assets/logo.svg")
        self.svg_widget.setGeometry(50, 50, 200, 200)
        self.svg_widget.setMinimumSize(32, 32)
        self.svg_widget.setMaximumSize(64, 64)
        self.horizontalLayout.insertWidget(1, self.svg_widget)
        self.login_button.clicked.connect(self.ok)
        self.register_button.clicked.connect(self.okk)

    def okk(self):
        self.register = RegisterWidget(self)
        self.register.show()
        self.hide()

    def ok(self):
        self.login = LoginWidget(self)
        self.login.show()
        self.hide()