import sqlite3
import re
import urllib.request
from bs4 import BeautifulSoup

LINK_URL = 'https://miet.ru/structure/e/3110'
MIET_LINK = 'https://miet.ru'

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    cathedras = soup.find('div', class_ = 'news-detail')
    links = cathedras.find('ul')

    cathedraLinks = []

    for link in links.find_all('li'):
        cathedraLinks.append({
            'cathedra': link.find('a').text,
            'link': MIET_LINK + link.find('a').get('href')
        })
    return cathedraLinks


def parse(html, cathedraName, link):
    soup = BeautifulSoup(html, 'html.parser')
    information = soup.find('div', {'id': 'eli_detail'})

    cathedraInfo = []

    mailPattern = r'\w+@\w+.\w{1,4}'
    hallPattern = r':\s*(\d{4}\w*)'
    phonePattern = r'(\W\d{3}\W\s\d{3}-\d{2}-\d{2})\s*'
    cipherPattern = r'([А-Яа-я]*[-]?[1-2]?)*'

    phone = re.search(phonePattern, str(information))
    mail = re.search(mailPattern, str(information))
    hall = re.search(hallPattern, str(information))
    cipher = re.search(cipherPattern, cathedraName)

    cathedraInfo.append({
        'cathedra': cathedraName,
        'cipher': cipher.group(0),
        'head': information.find('a').text,
        'phone': phone.group(0) if phone else 'не указан',
        'mail': mail.group(0) if mail else 'не указан',
        'hall': hall.group(0)[2:] if hall else 'не указана',
        'link': link
    })
    return cathedraInfo


def save(cathedras, db_file):
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Создаём таблицу users, если она не существует
    cursor.execute("""CREATE TABLE IF NOT EXISTS cathedras
                                      (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        cathedra TEXT,
                                        cipher TEXT,
                                        head TEXT,
                                        phone TEXT,
                                        hall TEXT,
                                        mail TEXT,
                                        link TEXT
                                      )""")

    db.commit()

    for cathedra in cathedras:
        cursor.execute(
            'INSERT INTO cathedras (cathedra, head, phone, hall, mail, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (cathedra['cathedra'], cathedra['cipher'], cathedra['head'], cathedra['phone'], cathedra['hall'], cathedra['mail'],
             cathedra['link']))

    db.commit()

def main():
    links = get_links(get_html(LINK_URL))
    parser = []

    for link in links:
        parser.extend(parse(get_html(link['link']), link['cathedra'], link['link']))

    save(parser, 'cathedras.db')


if __name__ == '__main__':
    main()