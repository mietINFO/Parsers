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
    departments = soup.find('div', class_ = 'news-detail')
    links = departments.find('ul')

    departmentLinks = []

    for link in links.find_all('li'):
        departmentLinks.append({
            'department': link.find('a').text,
            'link': MIET_LINK + link.find('a').get('href')
        })
    return departmentLinks


def parse(html, departmentName, link):
    soup = BeautifulSoup(html, 'html.parser')
    information = soup.find('div', {'id': 'eli_detail'})

    departmentInfo = []

    mailPattern = r'\w+@\w+.\w{1,4}'
    hallPattern = r':\s*(\d{4}\w*)'
    phonePattern = r'(\W\d{3}\W\s\d{3}-\d{2}-\d{2})\s*'
    cipherPattern = r'([А-Яа-я]*[-]?[1-2]?)*'

    phone = re.search(phonePattern, str(information))
    mail = re.search(mailPattern, str(information))
    hall = re.search(hallPattern, str(information))
    cipher = re.search(cipherPattern, departmentName)

    departmentInfo.append({
        'department': departmentName,
        'cipher': cipher.group(0).upper(),
        'head': information.find('a').text,
        'phone': phone.group(0) if phone else 'не указан',
        'mail': mail.group(0) if mail else 'не указан',
        'hall': hall.group(0)[2:] if hall else 'не указана',
        'link': link
    })
    return departmentInfo


def save(departments, db_file):
    db = sqlite3.connect(db_file)
    cursor = db.cursor()

    # Создаём таблицу users, если она не существует
    cursor.execute("""CREATE TABLE IF NOT EXISTS departments
                                      (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                        department TEXT,
                                        cipher TEXT,
                                        head TEXT,
                                        phone TEXT,
                                        hall TEXT,
                                        mail TEXT,
                                        link TEXT
                                      )""")

    db.commit()

    for department in departments:
        cursor.execute(
            'INSERT INTO departments (department, cipher, head, phone, hall, mail, link) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (department['department'], department['cipher'], department['head'], department['phone'], department['hall'], department['mail'],
             department['link']))

    db.commit()

def main():
    links = get_links(get_html(LINK_URL))
    parser = []

    for link in links:
        parser.extend(parse(get_html(link['link']), link['department'], link['link']))

    save(parser, 'departments.db')


if __name__ == '__main__':
    main()