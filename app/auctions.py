import requests
from re import findall
from configparser import ConfigParser
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from time import sleep
from random import randint
from app.db import DB


class Auctions(object):
    def __init__(self):
        self.__config = ConfigParser()
        self.__config.read('app/config')
        self.__db = DB()
        self.__retries = 0
        self.__max_retries = int(self.__config.get('komornik.pl', 'max_retries'))

    def get_auctions(self, page=None):
        html = self.__get_auctions_page(page)
        auctions = self.__parse_auctions_page(html)
        return auctions

    def set_auctions(self, auctions):
        for auction in auctions:
            self.__db.insert(table='auctions', data=auction, ignore_duplicates=True)

    def __get_auctions_page(self, page=None):
        ua = UserAgent()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
            'Host': 'licytacje.komornik.pl',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'User-Agent': ua.random,
        }
        url = self.__config.get('komornik.pl', 'auctions_page') if not page else self.__config.get('komornik.pl', 'auctions_page') + '?page=' + str(page)
        print('Getting %s' % url)
        try:
            response = requests.get(url, headers=headers, timeout=int(self.__config.get('komornik.pl', 'timeout')))
        except requests.exceptions.ReadTimeout:
            if self.__retries < self.__max_retries:
                self.__retries += 1
                sleep(randint(5, 10))
                return self.__get_auctions_page(page)
            else:
                raise Exception('Timeout. Nie pobrano strony')
        if response.status_code == 200:
            return response.text
        elif self.__retries < self.__max_retries:
            self.__retries += 1
            sleep(randint(5, 10))
            return self.__get_auctions_page(page)
        else:
            raise Exception('Nie pobrano strony')

    @staticmethod
    def __parse_auctions_page(html):
        auctions = []
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find('table', 'table').find_all('tr')
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 7:
                auctions.append({
                    # 'lp': cells[0].get_text().strip(),
                    'bailiff_name': cells[1].get_text().strip(),
                    'signature': cells[2].get_text().strip(),
                    'kw_number': cells[3].get_text().strip(),
                    'type': cells[4].get_text().strip(),
                    'address': cells[5].get_text().strip(),
                    'id': findall('\d+', cells[6].find('a')['href'])[0],
                })
        return auctions
