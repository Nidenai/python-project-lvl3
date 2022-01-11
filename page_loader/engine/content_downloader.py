import os
from urllib.parse import urljoin, urlparse

import requests as re
from bs4 import BeautifulSoup as bs
from loguru import logger

from page_loader.engine.auxiliary import existing_path, check_response


def finder(file, source, url):  # поиск всех ссылок и запихивание их в список
    result = []
    content = open(file, 'r', encoding='utf-8').read()
    soup = bs(content, 'html.parser')
    tag, arg = source
    for link in soup.find_all(tag):
        if link.get(arg) is not None:
            if not link.get(arg).startswith('http'):
                result.append(urljoin(url, link.get(arg)))
            else:
                result.append(link.get(arg))
    return result


def download_content(url, path_=os.getcwd()):  # скачивание контента по ссылке
    check_response(url)
    existing_path(path_)
    filename = naming_file(url)
    filepath = os.path.join(path_, filename)
    with re.get(url, stream=True) as q:
        with open(filepath, 'wb+') as downloaded_file:
            for chunk in q.iter_content(chunk_size=128):
                downloaded_file.write(chunk)
    downloaded_file.close()


def naming_file(url):  # именование файла для сохранения его в папку с ресурсом
    v = str(url)
    v = v.replace('https://', '')
    v = v.replace('http://', '')
    v = v.replace('www.', '')
    v = v.replace('?', '-')
    v = v.replace('/', '-')
    v = v.replace('&', '-')
    v = v.replace(':', '-')
    if v.startswith('--'):
        v = v.replace('--', '', 1)
    elif v.startswith('-'):
        v = v.replace('-', '', 1)
    else:
        pass
    result = v
    return result


def replace(file, source):  # замена ссылки в интернете на
    # путь к ресурсу в странице
    tag, arg = source
    with open(file, 'r', encoding='utf-8') as fp:
        content = fp.read()
        soup = bs(content, "html.parser")
        for link in soup.find_all(tag):
            v = link.attrs
            q = v.get(arg)
            v[arg] = naming_path_to_source(q, format_path_to_source(file))
    with open(file, 'w+', encoding='utf-8') as k:
        k.write(str(soup))


def format_path_to_source(file):
    file = os.path.normpath(file)
    file = file.split(os.sep)
    return file[-1]


def naming_path_to_source(url, file):  # функция создает имя папки,
    # основываясь на имени файла
    f = file.replace('.html', '') + '_files'
    return os.path.join(f, naming_file(url))


def parsing(file, source, url, path_=os.getcwd()):  # объединяющая функция
    # для скачивания и замены
    logger.remove()
    logger.add('debug.json', format='{time}, {level}, {message}',
               level="DEBUG", rotation='100 Kb')
    data = check_resourse(finder(file, source, url), url)
    logger.debug(data)
    for url in data:
        download_content(url, path_)
    replace(file, source)


def check_resourse(list_, url_resourse):
    result = []
    for url_base in list_:
        u = urlparse(url_base)
        v = urlparse(url_resourse)
        logger.debug(u.netloc)
        logger.debug(v.netloc)
        if u.netloc == v.netloc:
            result.append(url_base)
    return result
