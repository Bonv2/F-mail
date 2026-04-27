import sys

from PyQt6.QtWidgets import QApplication

from uis.welcome_widget import WelcomeWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WelcomeWidget()
    ex.show()
    ex.post_show()
    sys.exit(app.exec())