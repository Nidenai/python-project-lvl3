import os
import sys

import requests
from loguru import logger
from tqdm import tqdm

from page_loader.content import find_content, \
    create_filename_for_file, replace_content
from page_loader.exceptions import check_url_response, is_path_exist

IMG = ('img', 'src')
SCRIPT = ('script', 'src')
LINK = ('link', 'href')
LIST_ = [IMG, SCRIPT, LINK]

logger.remove()
logger.add(sys.stdout, format="{message}", level="INFO")


def create_html_catalog(catalog):
    """Функция создает каталог для ресурсов страницы"""
    name = catalog.replace('.html', '_files')
    if not os.path.exists(name):
        os.mkdir(name)
    else:
        pass


def download_url(url, path_=os.getcwd(), filename=None):
    """Функция скачивает контент по ссылке,
    по умолчанию в рабочую директорию"""
    is_path_exist(path_)
    check_url_response(url)
    if filename is None:
        filename = create_filename_for_file(url)
    filepath = os.path.join(os.getcwd(), os.path.normpath(path_), filename)
    with requests.get(url, stream=True) as temp:
        with open(filepath, 'wb+') as downloaded_file:
            for chunk in temp.iter_content(chunk_size=128):
                downloaded_file.write(chunk)


def download(url, path_=os.getcwd()):
    try:
        filename = create_filename_for_file(url)
        download_url(url, path_, filename)
        logger.info(f'Resource by {url}] was downloaded: {filename}')
        filepath = os.path.join(os.getcwd(), os.path.normpath(path_), filename)
        create_html_catalog(filepath)
        catalog = os.path.normpath(filepath).replace('.html', '_files')
        catalog_name = os.path.basename(str(catalog))
        downloaded_list = []
        for item in tqdm(LIST_, desc='Getting resourses'):
            sample = find_content(filepath, item, url)
            downloaded_list = downloaded_list + sample
        replace_content(filepath, LIST_, url, catalog_name)
        for link in tqdm(downloaded_list, desc='Download Files', unit=' kb'):
            download_url(link, catalog)
        logger.info(f"Done. You can open saved page from: {filepath}")
        return filepath
    except Exception:
        raise TypeError('Ошибка')
