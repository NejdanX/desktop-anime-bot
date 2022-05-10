from login_form import Ui_LoginWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from Constants import DB_FILE_NAME
from Register import Registration
from Client import Client
from Bot import Bot
import sys
import sqlite3
import hashlib


class Login(QMainWindow, Ui_LoginWindow):
    def __init__(self):
        self.con = sqlite3.connect(DB_FILE_NAME)
        super(Login, self).__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.btn_sign_in.clicked.connect(self.sign_in)
        self.label_check_in.clicked.connect(self.check_in)

    def sign_in(self):
        """Авторизация пользователя и выдача соответствующих прав"""
        cur = self.con.cursor()
        # Хэшируем и сравниваем хэш в БД и введенный
        password = hashlib.sha512(self.input_password.text().encode()).hexdigest()
        is_correct_user = cur.execute('''
                                SELECT COUNT(username) FROM User
                                    WHERE username = ? AND password = ?''',
                                      (self.input_login.text().lower(), password)).fetchall()
        if not is_correct_user[0][0]:
            self.statusBar().showMessage('Неверный логин или пароль')
        else:
            self.chat = Client(self, Bot('Bot', '\\'), self.input_login.text())
            self.chat.show()
            self.chat.load_previous_data()
            self.hide()

    def check_in(self):
        """Открывает форму на регистрацию"""
        self.register = Registration()
        self.register.setWindowModality(Qt.ApplicationModal)
        self.register.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login()
    with open('static/css/dark.qss', 'r', encoding='utf8') as file:
        app.setStyleSheet(file.read())
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())