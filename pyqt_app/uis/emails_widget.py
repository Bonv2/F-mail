import requests
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QPixmap

from uis.single_email_widget import EmailSingleWidget
from uis.email_write_widget import EditEmailWidget
from uis.compiled.mailbox import Ui_MainWindow
import json
import base64


def base64_to_pixmap(base64_string):
    # 1. Decode the base64 string into bytes
    img_data = base64.b64decode(base64_string)

    # 2. Create an empty QPixmap and load the byte data
    pixmap = QPixmap()
    pixmap.loadFromData(img_data)

    return pixmap


class EmailsWidget(QMainWindow, Ui_MainWindow):
    def __init__(self, welcome_screen):
        super().__init__()
        self.opened_mail = "recieved"
        with open("do_not_share.json", "r") as file:
            data = json.load(file)
        self.session = data["sc"]
        with open("config.json", "r") as file:
            data = json.load(file)
        self.url = data["server_url"]
        self.setupUi(self)
        self.setWindowTitle("Emails")
        self.user_info = requests.get(self.url + "api/this_user", cookies={"session": self.session}).json()["users"][0]
        self.welcome_screen = welcome_screen
        self.emails = []
        self.initUI()

    def write(self):
        self.answer_widget = EditEmailWidget(self.session,
                                             parent=self)
        self.answer_widget.show()

    def initUI(self):
        self.svg_widget = QSvgWidget("assets/logo.svg")
        self.svg_widget.setGeometry(50, 50, 200, 200)
        self.svg_widget.setMinimumSize(32, 32)
        self.svg_widget.setMaximumSize(32, 32)
        self.horizontalLayout.insertWidget(0, self.svg_widget)
        self.logout_button.clicked.connect(self.logout)
        self.write_button.clicked.connect(self.write)

        displayname = self.user_info["displayname"]
        username = self.user_info["username"]
        self.displayname_label.setText(f"{displayname} ({username})")
        self.sent_emails_button.clicked.connect(self.see_sent)
        self.recieved_emails_button.clicked.connect(self.see_recieved)

        try:
            image = self.user_info["pfp"]
            image = base64_to_pixmap(image)
            self.pfp_label.setPixmap(image)
            self.pfp_label.setScaledContents(True)
            self.pfp_label.setMinimumSize(32, 32)
            self.pfp_label.setMaximumSize(32, 32)
        except Exception:
            self.pfp_label.close()


        self.update_emails()

    def see_sent(self):
        self.opened_mail = "sent"
        self.emailsGroup.setTitle("Почта (Отправленная)")
        self.update_emails()

    def see_recieved(self):
        self.opened_mail = "recieved"
        self.emailsGroup.setTitle("Почта (Полученная)")
        self.update_emails()

    def update_emails(self):
        emails = requests.get(self.url + "api/emails", cookies={"session": self.session})
        if emails.status_code != 200:
            print("ERROR")
        data = emails.json()["emails"]
        for email in self.emails:
            email.close()
        self.emails.clear()

        for email in data:
            if self.opened_mail == "recieved" and email["receiver_username"] == self.user_info["username"]:
                widgt = EmailSingleWidget(self.session, email, self)
                self.scrollAreaWidgetContents.layout().addWidget(widgt)
                self.emails.append(widgt)
            elif self.opened_mail == "sent" and email["sender_username"] == self.user_info["username"]:
                widgt = EmailSingleWidget(self.session, email, self)
                self.scrollAreaWidgetContents.layout().addWidget(widgt)
                self.emails.append(widgt)

    def logout(self):
        with open("do_not_share.json", "r") as file:
            data = json.load(file)
        data["sc"] = ""
        with open("do_not_share.json", "w") as file:
            json.dump(data, file)
        self.welcome_screen.show()
        self.close()