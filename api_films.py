from kinopoisk_dev import KinopoiskDev
import requests
from bs4 import BeautifulSoup


def parse_date(lst: list[str]) -> str:
    new_date = ''
    for q in range(len(lst) - 1, -1, -1):
        new_date += lst[q] + '.'
    return new_date[:len(new_date) - 1]


TOKEN = 'V2FA1VF-NG04EC6-MX05S5P-G999ZNZ'
# headers = {'X-API-KEY': TOKEN}

kp = KinopoiskDev(token=TOKEN)

# Ищем страницу со списком актеров на кинопоиске, где есть искомый актер
actor_request = ''
url_total = ''
while url_total == '':
    page = 1
    actor_request = input('Введите имя актера/актрисы на русском или английском языках (если актер из России - '
                          'использовать только русский язык): ').title()  # Вводим имя актера
    while page <= 50:
        url = 'https://www.kinopoisk.ru/popular/names/page/'
        url += str(page) + '/'
        temp_info = str(requests.get(url).text)
        if actor_request in temp_info:
            url_total += url
            break
        else:
            page += 1
        if url_total == '' and page == 50:
            print('Имя актера/актрисы написано некорректно, либо актера/актрисы нет '
                  'на Кинопоиске. Попробйте изменить запрос')

# Нашли страницу, теперь достаём ID актера для последующего поиска фильмов с ним
pars_info = BeautifulSoup(requests.get(url_total).text, 'html.parser').find_all('div', class_='el')
act_id_str = ''
for element in pars_info:
    if actor_request in str(element):
        for i in element.a['href']:
            if i.isdigit():
                act_id_str += i
actor_id = int(act_id_str)

# Подключаемся через API к Кинопоиску и находим профиль актера по его ID
actor_info = kp.find_one_person(actor_id)


# Выдаем вводную информацию по актеру
birth_date = parse_date(actor_info.birthday[:10].split('-'))

death_date = actor_info.death
if death_date is None:
    death_date = 'Еще жив(а)'
else:
    death_date = parse_date(actor_info.death[:10].split('-'))


print(f'Имя: {actor_info.name}', f'Имя на английском языке: {actor_info.enName}',
      f'Дата рождения: {birth_date}', f'Дата смерти: {death_date}', f'Возраст: {actor_info.age}',
      f'Пол: {actor_info.sex}', f'Фото: {actor_info.photo}', f'Рост: {actor_info.growth} см', sep='\n')
print()

# Выводим фильмы, где снимался актер, с дополнительной информацией
for el in actor_info.movies:
    film_rus = el.name
    if film_rus is None:
        film_rus = '-'
    film_en = el.alternativeName
    if film_en is None:
        film_en = '-'
    role = el.description
    if role is None:
        role = '-'
    link = 'https://www.kinopoisk.ru/film/' + str(el.id) + '/'
    rating = el.rating
    if rating is None:
        rating = '-'

    print(f'Название фильма: {film_rus}', f'Название фильма на английском языке: {film_en}',
          f'Роль: {role}', f'Ссылка на фильм: {link}', f'Рейтинг: {rating}', sep='\n')
    print()
