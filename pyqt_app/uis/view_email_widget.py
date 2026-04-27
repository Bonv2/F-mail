from PyQt6.QtWidgets import QWidget

from uis.email_write_widget import EditEmailWidget
from uis.compiled.email_view import Ui_Form

import requests
import json


class ViewEmailWidget(QWidget, Ui_Form):
    def __init__(self, session, data, parent=None):
        super(QWidget, self).__init__()
        self.parent_w = parent
        self.data = data
        self.session = session
        self.setupUi(self)
        self.setWindowTitle('Email View')
        self.initUI()

    def answer(self):
        self.answer_widget = EditEmailWidget(self.session, reciever=self.data["sender_username"], title=self.data["title"],
                                             parent=self.parent_w)
        self.answer_widget.show()
        self.close()

    def initUI(self):
        title = self.data["title"]
        content = self.data["contents"]
        sender_username = self.data["sender_username"]
        reciever_username = self.data["receiver_username"]
        self.content_label.setText(content)
        self.title_label.setText(title)
        self.sender_label.setText(sender_username)
        self.reciever_label.setText(reciever_username)

        self.close_button.clicked.connect(self.close)
        self.answer_button.clicked.connect(self.answer)

        with open("config.json", "r") as file:
            data = json.load(file)
        self.url = data["server_url"]

        this_user = requests.get(self.url + "api/this_user", cookies={"session": self.session}).json()["users"][0]
        if this_user["username"] == sender_username:
            self.sender_label.setText(f"{sender_username} (Вы)")
        if this_user["username"] == reciever_username:
            self.reciever_label.setText(f"{reciever_username} (Вы)")