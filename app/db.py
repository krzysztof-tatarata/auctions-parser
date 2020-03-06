import pymysql
from configparser import ConfigParser


class DB(object):
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('app/config')
        self.db = None
        self.connect()

    def connect(self):
        hostname = self.config.get('db', 'hostname')
        username = self.config.get('db', 'username')
        password = self.config.get('db', 'password')
        database = self.config.get('db', 'database')

        conn = pymysql.connect(host=hostname, user=username, passwd=password, db=database, connect_timeout=3000)
        conn.autocommit(True)
        self.db = conn.cursor(pymysql.cursors.DictCursor)
        return self.db

    def insert(self, table, data, ignore_duplicates=False):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        try:
            self.db.execute(sql, list(data.values()))
        except pymysql.err.IntegrityError:
            if not ignore_duplicates:
                raise
