from simplegmail import Gmail
from jinja2 import Environment, PackageLoader, select_autoescape
from configparser import ConfigParser
from app.db import DB


class Notification(object):
    __auction_headers = {
        'id': 'ID',
        'bailiff_name': 'Nazwa kancelarii',
        'signature': 'Sygnatura',
        'kw_number': 'Numer KW',
        'type': 'Rodzaj',
        'address': 'Adres',
        'parse_dt': 'Data pobrania',
        'url': 'Link'
    }

    def __init__(self):
        self.__config = ConfigParser()
        self.__config.read('app/config')
        self.__db = DB()

    def get_notifications(self):
        sql = 'SELECT * FROM notifications WHERE active = 1'
        self.__db.cursor.execute(sql)
        results = self.__db.cursor.fetchall()
        return results

    def send_notification(self, notification, auctions):
        link_prefix = self.__config.get('komornik.pl', 'link_prefix')
        env = Environment(
            loader=PackageLoader('app', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('notification_mail.html')
        msg_html = template.render(notification=notification, auctions=auctions,
                                   auction_headers=self.__auction_headers, link_prefix=link_prefix)
        gmail = Gmail()
        params = {
            "to": notification['email'],
            "sender": self.__config.get('gmail', 'sender'),
            "subject": self.__config.get('gmail', 'subject'),
            "msg_html": msg_html,
            "msg_plain": "Hi\nThis is a plain text email.",
            "signature": True  # use my account signature
        }
        # print(msg_html)
        message = gmail.send_message(**params)
        pass

    def search_auctions(self, type, pattern, last_check_dt):
        sql = 'SELECT * FROM auctions WHERE {} LIKE "%{}%" AND parse_dt > "{}" ORDER BY id DESC'\
            .format(type, pattern, last_check_dt)
        self.__db.cursor.execute(sql)
        results = self.__db.cursor.fetchall()
        return results

    def update_notification_time(self, id):
        sql = 'UPDATE notifications SET last_check_dt = NOW() WHERE id = %s'
        return self.__db.cursor.execute(sql, id)

if __name__ == "__main__":
    n = Notification()
    notifications = n.get_notifications()
    for notification in notifications:
        auctions = n.search_auctions(type=notification['type'], pattern=notification['pattern'],
                                     last_check_dt=notification['last_check_dt'])
        if auctions:
            n.send_notification(notification=notification, auctions=auctions)
        n.update_notification_time(notification['id'])