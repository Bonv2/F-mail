from PyQt6.QtWidgets import QWidget

from uis.view_email_widget import ViewEmailWidget
from uis.email_write_widget import EditEmailWidget
from uis.compiled.single_email import Ui_Form


class EmailSingleWidget(QWidget, Ui_Form):
    def __init__(self, session, data, parent=None):
        super(QWidget, self).__init__()
        self.parent_w = parent
        self.data = data
        self.session = session
        self.setupUi(self)
        self.setWindowTitle("View single email")
        self.initUI()

    def initUI(self):
        title = self.data["title"]
        content = self.data["contents"][:64] + "..."
        sender_username = self.data["sender_username"]
        self.content_label.setText(content)
        self.title_label.setText(title)
        self.groupBox.setTitle(sender_username)

        self.open_button.clicked.connect(self.open_mail)
        self.answer_button.clicked.connect(self.answer)

    def answer(self):
        self.answer_widget = EditEmailWidget(self.session, reciever=self.data["sender_username"],
                                             title=self.data["title"],
                                             parent=self.parent_w)
        self.answer_widget.show()

    def open_mail(self):
        self.view_widget = ViewEmailWidget(self.session, self.data, parent=self.parent_w)
        self.view_widget.show()