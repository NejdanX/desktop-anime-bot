import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem, QLabel
from read_message_form import Ui_MessageRead


class MessageRead(QWidget, Ui_MessageRead):
    def __init__(self, item):
        super(MessageRead, self).__init__()
        self.setupUi(self)
        sheet = 'a:link {color: rgb(77, 231, 231);}'
        image_label = QLabel()
        image = item.icon().pixmap(200, 300)
        image_label.setPixmap(image)
        image_label.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(image_label, 0, 0)
        self.message_text.document().setDefaultStyleSheet(sheet)
        self.message_text.setAlignment(Qt.AlignJustify)
        self.parse_item(item)

    def parse_item(self, item):
        for string in item.text().split('\n'):
            row = ''
            if 'http' in string:
                for word in string.split():
                    if word.startswith('http'):
                        name = word.split('(')[-1]
                        name = name[:name.find(')')]
                        if 'http' not in name:
                            word = '<a href={}>{}</a>'.format(word, name)
                        else:
                            word = '<a href={}>{}</a>'.format(word, word)
                    row += word + ' '
                self.message_text.append(row.rstrip())
            else:
                if not string.startswith('    '):
                    string = '\t' + string
                if string.startswith('    '):
                    string = '\t\t' + string.strip()
                self.message_text.append(string.rstrip())
        text_cursor = self.message_text.textCursor()
        text_cursor.setPosition(0)
        self.message_text.setTextCursor(text_cursor)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('static/css/dark.qss', 'r', encoding='utf8') as file:
        app.setStyleSheet(file.read())
    ex = MessageRead(QListWidgetItem('Hello, world!\nHow are you?'))
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())