import json
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QListWidgetItem
from Constants import COMMANDS_HELP, COMMANDS
from random import randint
from datetime import datetime
from nltk import edit_distance  # Расчёт расстояния между словами, так можно исправить простейшие очепятки


class Bot:
    def __init__(self, name, command_symbol):
        self.name = name
        self.url = 'https://shikimori.one/api'
        self.main_page = 'https://shikimori.one'
        self.command_symbol = command_symbol
        self.height_message_item = 600
        self.cash_requests = {}

    def set_name(self, new_name):
        self.name = new_name

    def get_name(self):
        return self.name

    def set_command_symbol(self, new_command_symbol):
        self.command_symbol = new_command_symbol

    def get_command_symbol(self):
        return self.command_symbol

    def help(self, command):
        return COMMANDS_HELP.get(command, 'Не удалось распознать команду')

    def answer(self, width, height, message):
        new_item = QListWidgetItem(message)
        new_item.setTextAlignment(Qt.AlignJustify)
        new_item.setSizeHint((QSize(width, height)))
        return new_item

    def reaction(self, client, last_message):
        """Реакция на сообщение пользователя"""
        self.client = client
        # if not last_message.startswith(self.get_command_symbol()) and not last_message.startswith(self.get_name()):
        #     self.client.chat.addItem('Хм...')  # TODO Random Phrase
        #     return
        last_message = last_message.split()
        if COMMANDS['HELP'] in last_message:
            new_item = QListWidgetItem()
            new_item.setTextAlignment(Qt.AlignJustify)
            if len(last_message) == 2:
                # Краткая информация о боте и командах
                answer = self.help(COMMANDS['HELP'])
                new_item.setText(answer)
                new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, 250)))
                return new_item
            else:
                # Более подробная информация о конкретной команде
                answer = self.help(' '.join(last_message[2:]))
                height = 30 if answer == 'Не удалось распознать команду' else 150
                new_item.setText(answer)
                new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, height)))
                return new_item
        if COMMANDS["BOT_NAME"] in last_message:
            return self.answer(self.client.chat.size().width() - 5, 30, 'Моё имя без истерик: ' + self.get_name())
        elif COMMANDS["SET_NAME"] in last_message:
            if len(last_message) != 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   'Некорректное имя. Имя должно состоять из одного слова.')
            new_name = last_message[2]
            self.set_name(new_name)
            self.client.set_command_text(self.client.labels)
            return self.answer(self.client.chat.size().width() - 5, 30, f'Имя бота была изменено на: {new_name}')
        elif COMMANDS["FIND"] in last_message:
            if len(last_message) < 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите название аниме.")
            anime_name = ' '.join(last_message[last_message.index(COMMANDS["FIND"]) + 1:]).lower()
            return self.take_data_with_handle_exception(self.find_anime_by_name, anime_name)
        elif COMMANDS["ALL_CHARACTERS"] in last_message:
            if len(last_message) < 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите название аниме.")
            anime_name = ' '.join(last_message[last_message.index(COMMANDS["ALL_CHARACTERS"]) + 1:]).lower()
            return self.take_data_with_handle_exception(self.find_all_characters_from_anime, anime_name)
        elif 'character' in last_message and 'from' in last_message:
            if len(last_message) < 5:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите персонажа и название аниме.")
            character, anime = last_message[2:last_message.index('from')], last_message[last_message.index('from') + 1:]
            character, anime = ' '.join(character), ' '.join(anime)
            return self.take_data_with_handle_exception(self.search_character_from_anime, character, anime)
        elif COMMANDS["RELATED_TO"] in last_message:
            if len(last_message) < 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите название аниме.")
            anime_name = ' '.join(last_message[last_message.index(COMMANDS["RELATED_TO"]) + 1:])
            return self.take_data_with_handle_exception(self.find_related_to_anime, anime_name)
        elif COMMANDS["SIMILAR"] in last_message:
            if len(last_message) < 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите название аниме.")
            count_anime = 10
            if 'count' in last_message:
                count_anime = int(last_message[-1])
                last_message = last_message[:-2]
            anime_name = ' '.join(last_message[last_message.index(COMMANDS["SIMILAR"]) + 1:])
            return self.take_data_with_handle_exception(self.find_similar_anime, anime_name, count_anime)
        elif COMMANDS["FRANCHISE"] in last_message:
            if len(last_message) < 3:
                return self.answer(self.client.chat.size().width() - 5, 30,
                                   "Некорректный запрос. Введите название аниме.")
            anime_name = ' '.join(last_message[last_message.index(COMMANDS["FRANCHISE"]) + 1:])
            return self.take_data_with_handle_exception(self.find_franchise, anime_name)
        elif COMMANDS["RANDOM"] in last_message:
            return self.take_data_with_handle_exception(self.random_anime)
        else:
            self.client.chat.addItem(self.answer(self.client.chat.size().width() - 5, 30, 'Да?'))
            return

    def take_data_with_handle_exception(self, function, *args):
        """Пытается получить данные или правильно обработать исключение"""
        apologize = 'Сервер не отвечает. Попробуйте сделать ваш запрос позже. Извините за неудобства!'
        try:
            return function(*args)
        except HTTPError as err:
            with open('static/logs/log.txt', 'a', encoding='utf8') as file:
                info = f'Date: {str(datetime.now())} User: {self.client.name}\n' \
                       f'Query: {function.__name__}\nCode: {err.code} {err.read()}\n\n'
                file.write(info)
            return self.answer(self.client.chat.size().width() - 5, 40, apologize)
        except URLError as err:
            with open('static/logs/log.txt', 'a', encoding='utf8') as file:
                info = f'Date: {str(datetime.now())} User: {self.client.name}\n' \
                       f'Query: {function.__name__}\nCode: {err.reason}\n\n'
                file.write(info)
            return self.answer(self.client.chat.size().width() - 5, 40, apologize)

    def take_json_data(self, url):
        """Пытается взять данные у сервера. Если сервер не дал данные,
        то записываем в логи проблему и извиняемся перед пользователем"""
        try:
            json_anime_information = json.loads(urllib.request.urlopen(url).read().decode('utf8'))
            return json_anime_information
        except HTTPError as err:
            with open('static/logs/log.txt', 'a', encoding='utf8') as file:
                info = f'Date: {str(datetime.now())} User: {self.client.name}\nCode: {err.code} {err.read()}\n\n'
                file.write(info)
            return {'error': 'Сервер не отвечает. Попробуйте сделать ваш запрос позже. Извините за неудобства!'}

    def find_similar_anime(self, anime, count):
        """Находит похожие аниме"""
        anime_id = self.take_anime_id(anime)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS['SIMILAR'] in self.cash_requests[anime_id]['commands']:
            json_anime_information = self.cash_requests[anime_id]['commands'][COMMANDS['SIMILAR']][1]
        else:
            json_anime_information = self.take_json_data(self.url + f"/animes/{anime_id}/similar")
        if json_anime_information.__class__.__name__ == 'dict' and json_anime_information.get('error'):
            info = json_anime_information['error']
            height = 30
        else:
            info = '\n\n'.join([self.anime_information(dictionary) for dictionary in json_anime_information[:count]])
            height = 215
        if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
            self.cash_requests[anime_id]['commands'].update({COMMANDS['SIMILAR']: ('', json_anime_information)})
        else:
            self.cash_requests[anime_id] = {'commands': {COMMANDS['SIMILAR']: ('', json_anime_information)}}
        return self.answer(self.client.chat.size().width() - 5, height, info)

    def find_franchise(self, anime):
        """Находит франшизу. Результат не кэширует"""
        anime_id = self.take_anime_id(anime)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS["FRANCHISE"] in self.cash_requests[anime_id]['commands']:
            json_anime_information = self.cash_requests[anime_id]['commands'][COMMANDS["FRANCHISE"]][1]
        else:
            json_anime_information = self.take_json_data(self.url + f"/animes/{anime_id}/franchise?order=year")
        if json_anime_information.__class__.__name__ == 'dict' and json_anime_information.get('error'):
            info = json_anime_information['error']
            height = 30
        else:
            if json_anime_information['nodes']:
                info = '\n\n'.join([self.franchise_information(item) for item in json_anime_information['nodes']])
                height = 230
            else:
                info = 'Не удалось найти франшизу'
                height = 30
        if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
            self.cash_requests[anime_id]['commands'].update({COMMANDS["FRANCHISE"]: ('', json_anime_information)})
        else:
            self.cash_requests[anime_id] = {'commands': {COMMANDS["FRANCHISE"]: ('', json_anime_information)}}
        return self.answer(self.client.chat.size().width() - 5, height, info)

    def random_anime(self):
        """Возвращает случайно найденное аниме. К сожалению, данного метода нет в API, т.ч. импровизируем"""
        if self.client.previous_random_data:
            id_random_anime_in_cash = []
            for id in list(self.cash_requests.keys())[-15:]:
                rd = self.cash_requests[id]['commands'].get(COMMANDS['RANDOM'])
                if rd:
                    id_random_anime_in_cash.append(rd[1]['id'])
                    if len(id_random_anime_in_cash) == self.client.previous_random_data:
                        break
            anime_id = id_random_anime_in_cash[-1]
            self.client.previous_random_data += 1
        else:
            json_anime_information = []
            while not json_anime_information:
                new_url = self.url + f"/animes?page={randint(1, 14000)}"
                json_anime_information = self.take_json_data(new_url)
                if json_anime_information.__class__.__name__ == 'dict' and json_anime_information.get('error'):
                    json_anime_information = []
            anime_id = json_anime_information[0]['id']
        if anime_id in self.cash_requests and COMMANDS['RANDOM'] in self.cash_requests[anime_id]['commands']:
            json_anime_information = self.cash_requests[anime_id]['commands'][COMMANDS['RANDOM']][1]
        else:
            json_anime_information = self.take_json_data(self.url + f"/animes/{anime_id}")
        if json_anime_information.__class__.__name__ == 'dict' and json_anime_information.get('error'):
            img = ''
            info = json_anime_information['error']
            new_item = QListWidgetItem(info)
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, 30)))
        else:
            url = self.main_page + json_anime_information['image']['original']
            img = urllib.request.urlopen(url)
            image = QPixmap()
            image.loadFromData(img.read())
            new_item = QListWidgetItem(QIcon(image), self.anime_information(json_anime_information))
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, self.height_message_item)))
        if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
            self.cash_requests[anime_id]['commands'].update({COMMANDS['RANDOM']: (img, json_anime_information)})
        else:
            self.cash_requests[anime_id] = {'commands': {COMMANDS['RANDOM']: (img, json_anime_information)}}
        return new_item

    def find_related_to_anime(self, anime):
        """Находит аниме, напрямую связанные с введенным"""
        anime_id = self.take_anime_id(anime)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS["RELATED_TO"] in self.cash_requests[anime_id]['commands']:
            return self.search_in_cash(anime_id, COMMANDS["RELATED_TO"], self.related_anime_information, 300)
        else:
            new_url = self.url + f"/animes/{anime_id}/related"
            json_anime_information = json.loads(urllib.request.urlopen(new_url).read().decode('utf8'))
            new_item = QListWidgetItem(self.related_anime_information(json_anime_information))
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, 300)))
            if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
                self.cash_requests[anime_id]['commands'].update({COMMANDS["RELATED_TO"]: ('', json_anime_information)})
            else:
                self.cash_requests[anime_id] = {'commands': {COMMANDS["RELATED_TO"]: ('', json_anime_information)}}
            return new_item

    def search_character_from_anime(self, character, anime):
        """Ищет персонажа character в anime"""
        anime_id = self.take_anime_id(anime)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS["ALL_CHARACTERS"] in self.cash_requests[anime_id]['commands']:
            # Проверяем, запрашивались ли персонажи из этого аниме до этого
            json_characters_information = self.cash_requests[anime_id]['commands'][COMMANDS["ALL_CHARACTERS"]][1]
        else:
            # Персонажей можно искать только через animes/id/roles,
            # так что просто запрашиваем данные о всех персонажах и уже там найдем нужного
            self.find_all_characters_from_anime(anime)
            json_characters_information = self.cash_requests[anime_id]['commands'][COMMANDS["ALL_CHARACTERS"]][1]
        character_id = self.search_character(json_characters_information, character)
        if character_id.__class__.__name__ == 'QListWidgetItem':
            return character_id
        if 'search_character' in self.cash_requests[anime_id]['commands'] and \
                self.cash_requests[anime_id]['commands']['search_character'].get(character_id) and \
                self.cash_requests[anime_id]['commands']['search_character'].get(character_id)[0]:
            json_character = self.cash_requests[anime_id]['commands']['search_character'][character_id]
            image = json_character[0]
            data = json_character[1]
            new_item = QListWidgetItem(QIcon(image), self.character_information(data))
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, self.height_message_item)))
            return new_item
        elif 'search_character' in self.cash_requests[anime_id]['commands'] and \
                self.cash_requests[anime_id]['commands']['search_character'].get(character_id):
            info_character = self.cash_requests[anime_id]['commands']['search_character'][character_id]
        else:
            url = self.url + f'/characters/{character_id}'
            info_character = json.loads(urllib.request.urlopen(url).read().decode('utf8'))
        img = urllib.request.urlopen(self.main_page + info_character['image']['original'])
        image = QPixmap()
        image.loadFromData(img.read())
        new_item = QListWidgetItem(QIcon(image), self.character_information(info_character))
        new_item.setTextAlignment(Qt.AlignJustify)
        new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, self.height_message_item)))
        if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
            if not self.cash_requests[anime_id]['commands'].get('search_character'):
                self.cash_requests[anime_id]['commands'].update({'search_character': {}})
            self.cash_requests[anime_id]['commands']['search_character'].update({character_id: (image, info_character)})
        else:
            self.cash_requests[anime_id] = {'commands': {'search_character': {character_id: (image, info_character)}}}
        return new_item

    def find_all_characters_from_anime(self, anime_name):
        """Находим аниме по ID и получаем всех персонажей"""
        anime_id = self.take_anime_id(anime_name)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS["ALL_CHARACTERS"] in self.cash_requests[anime_id]['commands']:
            return self.search_in_cash(anime_id, COMMANDS["ALL_CHARACTERS"], self.all_characters_by_rolls,
                                       self.height_message_item - 305)
        else:
            new_url = self.url + f"/animes/{anime_id}/roles"
            json_characters_information = json.loads(urllib.request.urlopen(new_url).read().decode('utf8'))
            all_characters = self.all_characters_by_rolls(json_characters_information)
            new_item = QListWidgetItem(all_characters)
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, self.height_message_item - 305)))
            if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
                self.cash_requests[anime_id]['commands'].update({
                    COMMANDS["ALL_CHARACTERS"]: ('', json_characters_information)})
            else:
                self.cash_requests[anime_id] = {'commands': {COMMANDS["ALL_CHARACTERS"]: ('', json_characters_information)}}
            return new_item

    def find_anime_by_name(self, anime_name):
        """Находит аниме по названию"""
        anime_id = self.take_anime_id(anime_name)
        if anime_id.__class__.__name__ == 'QListWidgetItem':
            return anime_id
        if anime_id in self.cash_requests and COMMANDS['FIND'] in self.cash_requests[anime_id]['commands'] and \
                self.cash_requests[anime_id]['commands'][COMMANDS['FIND']][0]:
            return self.search_in_cash(anime_id, COMMANDS['FIND'], self.anime_information, self.height_message_item)
        elif anime_id in self.cash_requests and COMMANDS['FIND'] in self.cash_requests[anime_id]['commands']:
            json_anime_information = self.cash_requests[anime_id]['commands'][COMMANDS['FIND']][1]
        else:
            new_url = self.url + f"/animes/{anime_id}"
            json_anime_information = json.loads(urllib.request.urlopen(new_url).read().decode('utf8'))  # А по id полную
        img = urllib.request.urlopen(self.main_page + json_anime_information['image']['original'])
        image = QPixmap()
        image.loadFromData(img.read())
        new_item = QListWidgetItem(QIcon(image), self.anime_information(json_anime_information))
        new_item.setTextAlignment(Qt.AlignJustify)
        new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, self.height_message_item)))
        if self.cash_requests.get(anime_id):  # Если аниме с таким id уже есть, то просто обновляем словарь
            self.cash_requests[anime_id]['commands'].update({COMMANDS['FIND']: (image, json_anime_information)})
        else:
            self.cash_requests[anime_id] = {'commands': {COMMANDS['FIND']: (image, json_anime_information)}}
        return new_item

    def take_anime_id(self, anime_name):
        """Находим аниме по имени и возвращаем его id"""
        url = self.url + f'/animes?search={quote(anime_name)}'
        anime = urllib.request.urlopen(url).read().decode('utf8')  # Получили не полную информацию по имени
        if anime == '[]':
            new_item = QListWidgetItem('Аниме с таким названием не найдено')
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, 30)))
            return new_item
        json_anime_information = json.loads(anime)
        return json_anime_information[0]['id']

    def anime_information(self, json_anime_information):
        """Получаем информацию об аниме"""
        if json_anime_information.get('description') is None:
            description = ''
        else:
            d = 'description'
            description = json_anime_information[d] if json_anime_information[d] else 'Нет данных'
            description = f'\n\n{description}\n'
        info = f'''Название: {json_anime_information['name']}({json_anime_information['russian']})
                            Рейтинг: {json_anime_information['score']}/10
                            Статус: {json_anime_information['status']}
                            Тип: {json_anime_information['kind']}
                            Релиз: {json_anime_information['aired_on']}
                            Вышло: {json_anime_information['released_on']}
                            {'Количество серий: ' + str(json_anime_information['episodes'])
        if json_anime_information['kind'] == 'tv' else ''}{self.clear_description(description)}
    {self.main_page + json_anime_information['url']}'''
        return info

    def character_information(self, json_info):
        """Предоставляет информацию о персонаже с описанием и произведениями, в который он участвовал"""
        description = json_info['description'] if json_info['description'] else 'Нет данных'
        was_in_the_works = self.character_works(json_info)
        info = f"Имя: {json_info['name']}({json_info['russian']})\n{self.main_page + json_info['url']}\n" \
               f"{self.clear_description(description)}\nУчаcтник:\n\n{was_in_the_works}\n"
        return info

    def franchise_information(self, json_info):
        """Краткая информация о франшизе упорядоченными по дате выхода (в запросе есть параметр order)"""
        info = f'''Название: {json_info['name']}
                                Тип: {json_info['kind']}
                                Выход: {json_info['year']}
        {self.main_page + json_info['url']}'''
        return info

    def related_anime_information(self, json_info):
        """Предоставляет краткую информацию о произведениях связанных с аниме"""
        animes = ''
        mangas = ''
        for info in json_info:
            if info['anime']:
                anime = info['anime']
                animes += f"АНИМЕ\nТип: {anime['kind']}\nТип связи: {info['relation']}\n" \
                          f"{anime['name']}\n{anime['russian']}\n"
                animes += f"{self.main_page + anime['url']}\n\n"
            elif info['manga']:
                manga = info['manga']
                mangas += f"МАНГА\nТип: {manga['kind']}\nТип связи: {info['relation']}\n" \
                          f"{manga['name']}\n{manga['russian']}\n"
                mangas += f"{self.main_page + manga['url']}\n\n"
        return animes + mangas

    def search_character(self, json_characters_information, character):
        """Ищем персонажа по id в json-файле, который мы получили по всем персонажам данного аниме"""
        character_id = 0
        for data in json_characters_information:
            if data['character'] is None:
                continue
            name = data['character']['name'].lower()
            r_name = data['character']['russian'].lower()
            character = character.lower()
            # Очепятки пытаемся найти
            if edit_distance(name, character) / len(name) < 0.35 or \
                    edit_distance(r_name, character) / len(r_name) < 0.35 or character in r_name or character in name:
                character_id = data['character']['id']
                break
        if not character_id:
            new_item = QListWidgetItem('Данный персонаж не найден')
            new_item.setTextAlignment(Qt.AlignJustify)
            new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, 30)))
            return new_item
        return character_id

    def all_characters_by_rolls(self, json_characters_information):
        """Удобное представление персонажей для вывода"""
        data = {}
        for dictionary in json_characters_information:
            if dictionary['character'] is None:
                continue
            data[dictionary['character']['id']] = {'name': dictionary['character']['name'],
                                                   'russian_name': dictionary['character']['russian'],
                                                   'roles': ' '.join(dictionary['roles'])
                                                   }
        result = {}
        for id in sorted(data, key=lambda x: data[x]['roles']):
            result[id] = f'{data[id]["roles"]} character\t' + f'{data[id]["name"]}({data[id]["russian_name"]})'
        return '\n'.join([info for info in result.values()])

    def character_works(self, json_info):
        """Возвращает аниме и мангу, в которых участвовал данный персонаж"""
        animes = ''
        mangas = ''
        for anime in json_info['animes']:
            animes += f"АНИМЕ\nТип: {anime['kind']}\n{anime['role']} character\n{anime['name']}\n{anime['russian']}\n"
            animes += f"{self.main_page + anime['url']}\n\n"
        for manga in json_info['mangas']:
            mangas += f"МАНГА\nТип: {manga['kind']}\n{manga['role']} character\n{manga['name']}\n{manga['russian']}\n"
            mangas += f"{self.main_page + manga['url']}\n\n"
        return animes + mangas

    def search_in_cash(self, anime_id, command, function, height):
        """Функция для поиска запросов в кеше"""
        info = function(self.cash_requests[anime_id]['commands'][command][1])
        if self.cash_requests[anime_id]['commands'][command][0]:
            new_item = QListWidgetItem(QIcon(self.cash_requests[anime_id]['commands'][command][0]), info)
        else:
            new_item = QListWidgetItem(info)
        new_item.setTextAlignment(Qt.AlignJustify)
        new_item.setSizeHint((QSize(self.client.chat.size().width() - 5, height)))
        return new_item

    def clear_description(self, description):
        """Чистит описание от всяких тегов и прочего мусора"""
        result = []
        for string in description.split('\n'):
            if 'url=' in string:
                start, end = string.find('http'), string.find(']')
                name = string[end + 1:string.find('[/url]')]
                url = string[start:end]
                print(url)
                string = string.replace(f'[url={url}]{name}[/url]', url + f'({name})')
            if '[/' in string:
                while '[/' in string:
                    string = string[:string.find('[')] + string[string.find(']') + 1:]
            if '[[' in string:
                string = string.replace('[[', '').replace(']]', '')
            result.append(string)
        return '\n'.join(result)
