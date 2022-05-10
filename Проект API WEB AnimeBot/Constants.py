DB_FILE_NAME = 'static/db/users_info.db'

JUST_HELP = 'Это бот, который помогает в поиске аниме. Боту доступны следующие команды:\n' \
            '\tfind_anime - поиск аниме по названию\n' \
            '\tset_new_name - установить новое имя ботe\n' \
            '\trandom_anime - случайное аниме\n' \
            '\tsimilar_anime_to - поиск похожих аниме\n' \
            '\tall_characters_from - вывод всех персонажей из аниме\n' \
            '\tcharacter from - вывод информацию о конкретном персонаже из аниме\n' \
            '\tfranchise - вывод информации о франшизе\n' \
            '\trelated_to - вывод аниме, напрямую связанных с запрошенным\n' \
            'Если хотите узнать более подробную информацию о команде, введите:\n\t{bot name}, help {command name}'
find_anime = 'Синтаксис: {name bot}, find_anime {name anime}\n' \
             'Альтернативный синтаксис: {command symbol}find_anime {name anime}\n' \
             'Выводит информацию об аниме: скриншот-превью, название, рейтинг, статус, тип, когда состоялся релиз,' \
             'дата выхода, количество эпизодов, описание и ссылку на страницу shikimori с данным аниме.'
set_new_name = 'Синтаксис: {name bot}, set_new_name {new name}\n' \
               'Альтернативный синтаксис: {command symbol}set_new_name {new name}\n' \
               'Задает новое имя боту, по которому вы можете к нему обращаться.'
random_anime = 'Синтаксис: {name bot}, random_anime\n' \
               'Альтернативный синтаксис: {command symbol}random_anime\n' \
               'Выводит случайное аниме, в формате: скриншот-превью, название, рейтинг, статус, тип, когда состоялся ' \
               'релиз, дата выхода, количество эпизодов, описание и ссылку на страницу shikimori с данным аниме.'
similar_anime_to = 'Синтаксис: {name bot}, similar_anime_to {name anime} [count] [{10}]\n' \
                   'Альтернативный синтаксис: {command symbol}similar_anime_to {name anime} [count] [{10}]\n' \
                   'Параметр [count] [{10}] - необязательный параметр\n' \
                   'По умолчанию, находит 10 похожих аниме, если это возможно. Если указать параметр [count]' \
                   'и число через пробел, найдет необходимое число похожих аниме, если это возможно.'
all_characters_from = 'Синтаксис: {name bot}, all_characters_from {name anime}\n' \
                      'Альтернативный синтаксис: {command symbol}all_characters_from {name anime}\n' \
                      'Выводит список всех персонажей из {name anime} в формате: Роль персонажа в аниме, имя.' \
                      'Сначала выводятся главные персонажи.'
character_from = 'Синтаксис: {name bot}, character {character name} from {name anime}\n' \
                 'Альтернативный синтаксис: {command symbol}character {character name} from {name anime}\n' \
                 'Выводит подробную информацию о персонаже из {name anime} в формате: Имя, ' \
                 'ссылка на страницу shikimori, описание, список аниме и манги с данным персонажам, также с ' \
                 'названиями, типом, ролью в произведении и ссылками на страницы shikimori на эти произведения.'
franchise = 'Синтаксис: {name bot}, franchise {name anime}\n' \
            'Альтернативный синтаксис: {command symbol}franchise {name anime}\n' \
            'Выводит информацию о франшизе, в которой состоит это аниме, упорядоченной по году выхода, в формате: ' \
            'название, тип, дата выхода, ссылка на страницу shikimori. Если аниме не состоит во франшизе, выводит ' \
            'сообщение, что франшизу найти не удалось.'
related_to = 'Синтаксис: {name bot}, related_to {name anime}\n' \
             'Альтернативный синтаксис: {command symbol}related_to {name anime}\n' \
             'Находит аниме и мангу, которые напрямую связаны с {name anime}. Выводит информацию в формате: ' \
             'сначала список аниме, с типом, типом связи, названием и ссылкой на страницу shikimori, а после мангу' \
             'в том же формате.'
COMMANDS_HELP = {
    'find_anime': find_anime,
    'set_new_name': set_new_name,
    'random_anime': random_anime,
    'similar_anime_to': similar_anime_to,
    'all_characters_from': all_characters_from,
    'character from': character_from,
    'franchise': franchise,
    'related_to': related_to,
    'help': JUST_HELP
}
