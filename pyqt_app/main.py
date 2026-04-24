import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtSvgWidgets import QSvgWidget



class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("welcome_screen.ui", self)
        self.setupUI()

    def setupUI(self):
        self.svg_widget = QSvgWidget("assets/logo.svg")
        self.svg_widget.setGeometry(50, 50, 200, 200)
        self.svg_widget.setMinimumSize(32, 32)
        self.svg_widget.setMaximumSize(64, 64)
        self.horizontalLayout.insertWidget(1, self.svg_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WelcomeWidget()
    ex.show()
    sys.exit(app.exec())