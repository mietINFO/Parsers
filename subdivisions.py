import sqlite3
import re
import urllib.request
from bs4 import BeautifulSoup

SUBDIVISIONS_LINK = 'https://miet.ru/structure/s/1619'
MIET_LINK = 'https://miet.ru'

def get_html(url):
    responce = urllib.request.urlopen(url)
    return responce.read()


def get_link(html):
    soup = BeautifulSoup(html, 'html.parser')
    information = soup.find('div', {'id': 'eli_link_list'})
    links = information.find('ul')

    subLinks = []

    for link in links.find_all('li'):
        subLinks.append({
            'name': link.find('a').text,
            'link': MIET_LINK + link.find('a').get('href')
        })
    return subLinks


def parse(html, subdivisionName, link):
    soup = BeautifulSoup(html, 'html.parser')
    information = soup.find('div', {'id': 'eli_detail'})

    subdivisionInfo = []

    mailPattern = r'\w+@\w+.\w{1,4}'
    hallPattern = r':\s*(\d{4}\w*)'
    phonePattern = r'(\W\d{3}\W\s\d{3}-\d{2}-\d{2})\s*'
    cipherPattern = r'\((.*?)\)'

    phone = re.search(phonePattern, str(information))
    mail = re.search(mailPattern, str(information))
    hall = re.search(hallPattern, str(information))
    cipher = re.search(cipherPattern, subdivisionName)
    head = information.find('a').text

    subdivisionInfo.append({
        'subdivision': subdivisionName,
        'cipher': cipher.group(1).upper(),
        'head': information.find('a').text if head else 'не указан',
        'phone': phone.group(0) if phone else 'не указан',
        'mail': mail.group(0) if mail else 'не указан',
        'hall': hall.group(0)[2:] if hall else 'не указана',
        'link': link
    })
    return subdivisionInfo


def save(subdivisions, db_file):
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Создаём таблицу users, если она не существует
    cursor.execute("""CREATE TABLE IF NOT EXISTS subdivisions
                                      (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        subdivision TEXT,
                                        head TEXT,
                                        phone TEXT,
                                        hall TEXT,
                                        mail TEXT,
                                        link TEXT
                                      )""")
    db.commit()

    for subdivision in subdivisions:
        cursor.execute(
            'INSERT INTO subdivisions (subdivision, head, phone, hall, mail, link) VALUES (?, ?, ?, ?, ?, ?)',
            (subdivision['subdivision'], subdivision['head'], subdivision['phone'], subdivision['hall'], subdivision['mail'],
             subdivision['link']))
    db.commit()


def main():
    links = get_link(get_html(SUBDIVISIONS_LINK))
    parser = []

    for link in links:
        parser.extend(parse(get_html(link['link']), link['name'], link['link']))
    parser[-1]['head'] = 'Кузнецов Григорий Александрович'
    parser[-3]['head'] = 'не указан'

    save(parser, 'subdivisions.db')


if __name__ == '__main__':
    main()