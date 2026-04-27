from PyQt6.QtWidgets import QWidget, QMessageBox

import requests
import json

from uis.compiled.email_write import Ui_Form


class EditEmailWidget(QWidget, Ui_Form):
    def __init__(self, session, parent=None, reciever=None, title=None):
        super(QWidget, self).__init__()
        self.parent_w = parent
        self.session = session
        self.reciever = reciever
        self.title = title
        self.setupUi(self)
        self.initUI()
        self.setWindowTitle('Email Write')

    def initUI(self):
        with open("config.json", "r") as file:
            data = json.load(file)
        self.url = data["server_url"]

        if self.reciever:
            self.reciever_edit.setText(self.reciever)
        if self.title:
            self.title_edit.setText(f"RE: {self.title}")

        this_user = requests.get(self.url + "api/this_user", cookies={"session": self.session}).json()["users"][0]
        self.sender_label.setText(f"{this_user["username"]} (Вы)")

        self.send_button.clicked.connect(self.send)

        self.close_button.clicked.connect(self.close)

    def send(self):
        reciever = self.reciever_edit.text()
        title = self.title_edit.text()
        content = self.content_edit.toPlainText()

        post = requests.post(self.url + "api/emails",
                             json={"receiver_username": reciever, "title": title, "contents": content},
                             cookies={"session": self.session})

        if post.status_code != 200:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"Error sending email, {post.status_code}")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            retval = msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(f"Success!")
            msg.setWindowTitle("It works!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            retval = msg.exec()
            self.parent_w.update_emails()
            self.close()