import sys
from chat_form import Ui_ChatForm
from PyQt5.QtCore import Qt, QSize
import os
from Constants import JUST_HELP, COMMANDS
from PyQt5.Qt import QColor
from PyQt5 import QtGui
from Bot import Bot
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QListWidget, QMenu, QAction
from MessageRead import MessageRead


class Client(QMainWindow, Ui_ChatForm):
    def __init__(self, login_window, bot, name):
        super(Client, self).__init__()
        self.name = name
        self.login_window = login_window
        self.bot = bot
        self.filename = f'data/{self.name}.json'
        self.previous_random_data = 1
        self.setupUi(self)
        self.queries = []
        self.set_ui()

    def set_ui(self):
        # Настраиваем контекстное меню при нажатии на сообщения ПКМ
        self.chat.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat.customContextMenuRequested.connect(self.context)
        self.chat.itemClicked.connect(self.open_message)
        self.btn_send.clicked.connect(self.send_message)
        self.chat.setWordWrap(Qt.TextWrapAnywhere)
        self.chat.setViewMode(QListWidget.IconMode)
        self.chat.setIconSize(QSize(200, 300))
        self.chat.setResizeMode(QListWidget.Adjust)
        self.label_login_as.setText(f'Вы вошли как {self.name}')
        self.label_exit.clicked.connect(self.close)
        self.labels = [self.label_related, self.label_find, self.label_similar, self.label_franchise,
                       self.label_all_characters, self.label_character, self.label_new_name, self.label_random]
        self.set_command_text(self.labels)
        for label in self.labels:
            label.clicked.connect(self.insert_label_text)

    def load_previous_data(self):
        """Загружаем данные из json-файла, который был заполнен в прошлом сеансе данного пользователя"""
        if os.path.exists(self.filename) and os.stat(self.filename).st_size > 0:
            with open(self.filename, 'r', encoding='utf8') as file:
                json_file = json.load(file)
            # Извлекаем из json-файла только данные
            self.queries = json_file['queries']
            # Записываем в кеш бота все данные, которые были получены из запросов пользователя
            # для следующего их быстрого поиска
            self.bot.cash_requests = {int(anime_id): data for anime_id, data in json_file.items()
                                      if anime_id != 'queries' and anime_id != 'bot name'}
            for query in self.queries:
                item = QListWidgetItem(query + '\n')
                item.setTextAlignment(Qt.AlignRight)
                item.setSizeHint(QSize(self.chat.size().width() - 5, 50))
                item.setBackground(QColor('#1e3232'))
                self.chat.addItem(item)
                answer = self.bot.reaction(self, query)
                if answer:
                    self.chat.addItem(answer)
            self.chat.scrollToBottom()
            self.bot.set_name(json_file['bot name'])
            self.set_command_text(self.labels)
        else:
            item = QListWidgetItem(f'Приветствую тебя, {self.name}!\n' + JUST_HELP + '\n')
            item.setTextAlignment(Qt.AlignJustify)
            item.setSizeHint(QSize(self.chat.size().width() - 5, 265))
            item.setBackground(QColor('#1e3232'))
            self.chat.addItem(item)
        self.previous_random_data = 0

    def context(self, point):
        """Контекстное меню"""
        self.point = point
        menu = QMenu()
        if self.chat.itemAt(point):
            open_message = QAction('Раскрыть сообщение', menu)
            delete_message = QAction('Удалить сообщение', menu)
            open_message.triggered.connect(self.open_message)
            delete_message.triggered.connect(self.delete_message)
            menu.addActions([open_message, delete_message])
        menu.exec(self.chat.mapToGlobal(point))

    def open_message(self, clicked_item=''):
        """Открывает сообщение с рабочими ссылками в новом окне по клику мыши или выбору из QMenu"""
        if self.sender().__class__.__name__ == 'QAction':
            item = self.chat.itemAt(self.point)
        else:
            item = clicked_item
        self.message = MessageRead(item)
        self.message.show()

    def delete_message(self):
        """Удаляет сообщение выбранное пользователем"""
        self.chat.takeItem(self.chat.row(self.chat.itemAt(self.point)))  # TODO удаление из кеша запросов

    def set_command_text(self, labels):
        name = self.bot.get_name()
        for label in labels:
            label.setText(name + label.text()[label.text().find(','):])

    def insert_label_text(self):
        self.text_message.setPlainText(self.sender().text())

    def send_message(self):
        """Отправка сообщения и получение ответа от пользователя"""
        item = QListWidgetItem(self.text_message.toPlainText() + '\n')
        item.setTextAlignment(Qt.AlignRight)
        item.setSizeHint(QSize(self.chat.size().width() - 5, 50))
        item.setBackground(QColor('#1e3232'))
        self.queries.append(self.text_message.toPlainText())
        self.chat.addItem(item)
        answer = self.bot.reaction(self, self.text_message.toPlainText())
        if answer:
            self.chat.addItem(answer)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """Сохраняем кэш и запросы в Json файл"""
        if self.queries:
            new_cash = {}
            for id in list(self.bot.cash_requests.keys()):
                new_cash[id] = {'commands': {}}
                for command in self.bot.cash_requests[id]['commands']:
                    if command == COMMANDS['RANDOM'] or command == COMMANDS['FIND']:
                        new_cash[id]['commands'][command] = ('', self.bot.cash_requests[id]['commands'][command][1])
                    elif command == 'search_character':
                        if not new_cash[id]['commands'].get(command):
                            new_cash[id]['commands'][command] = {}
                        for character_id in self.bot.cash_requests[id]['commands'][command]:
                            character_info = self.bot.cash_requests[id]['commands'][command][character_id][1]
                            new_cash[id]['commands'][command].update({character_id: ('', character_info)})
                    else:
                        new_cash[id]['commands'][command] = self.bot.cash_requests[id]['commands'][command]
            # Сохраняем последние 15 запросов (чтобы программа не запускалась слишком долго)
            new_cash.update({'queries': self.queries[-15:]})
            new_cash.update({'bot name': self.bot.get_name()})
            with open(self.filename, 'w') as f:
                json.dump(new_cash, f)
        self.login_window.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('static/css/dark.qss', 'r', encoding='utf8') as file:
        app.setStyleSheet(file.read())
    ex = Client(MessageRead(QListWidgetItem()), Bot('Bot', '\\'), 'client')
    ex.show()
    ex.load_previous_data()
    sys.excepthook = except_hook
    sys.exit(app.exec())
