from register_form import Ui_RegisterForm
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from Constants import DB_FILE_NAME
import Password
import sys
import sqlite3
import hashlib


class Registration(QWidget, Ui_RegisterForm):
    def __init__(self):
        self.con = sqlite3.connect(DB_FILE_NAME)
        super(Registration, self).__init__()
        self.setupUi(self)
        self.btn_register.clicked.connect(self.add_user)

    def add_user(self):
        """Добавляет пользователя в БД"""
        cur = self.con.cursor()
        if self.input_password.text() != self.input_repeat_password.text():
            self.message_label.setText('Ошибка: введенные пароли не совпадают')
            return
        username = self.input_username.text()
        password = self.input_password.text()
        correctness = self.check_correctness(username, password)
        if correctness == 'ok':
            # Шифруем пароль и заносим в БД
            password = hashlib.sha512(password.encode()).hexdigest()
            cur.execute(f'''INSERT INTO User(username, password)  
                            VALUES {(username.lower(), password)}''')
            self.con.commit()
            self.con.close()
            QMessageBox.information(self, 'Успешно', 'Регистрация прошла успешно', QMessageBox.Ok)
            self.close()
        else:
            self.message_label.setText(correctness)

    def check_correctness(self, username, password):
        """Проверяет наличие данного пользователя в БД и корректность введенных данных"""
        cur = self.con.cursor()
        if not username and not password:
            return 'Ошибка: не все поля заполнены'
        if Password.check_password(password) != 'ok':
            return Password.check_password(password)
        user_already_in = cur.execute('''
                                SELECT COUNT(username) FROM User
                                    WHERE username = ?''',
                                      (username.lower(),)).fetchall()
        if user_already_in[0][0]:
            return 'Ошибка: пользователь с таким логином есть в базе данных'
        return 'ok'

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:  # Установка echoMode для пароля
            if self.input_password.echoMode() == self.input_password.Password:
                self.input_password.setEchoMode(self.input_password.Normal)
                self.input_repeat_password.setEchoMode(self.input_repeat_password.Normal)
            else:
                self.input_password.setEchoMode(self.input_password.Password)
                self.input_repeat_password.setEchoMode(self.input_repeat_password.Password)
        if event.key() == Qt.Key_F2:  # Случайно сгенерированный пароль
            password = Password.generate_password(12)
            self.input_password.setText(password)
            self.input_repeat_password.setText(password)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Registration()
    with open('static/css/dark.qss', 'r', encoding='utf8') as file:
        app.setStyleSheet(file.read())
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
