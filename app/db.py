import pymysql
from configparser import ConfigParser


class DB(object):
    def __init__(self):
        self.__config = ConfigParser()
        self.__config.read('app/config')
        self.cursor = self.__connect()

    def __connect(self):
        hostname = self.__config.get('db', 'hostname')
        username = self.__config.get('db', 'username')
        password = self.__config.get('db', 'password')
        database = self.__config.get('db', 'database')

        conn = pymysql.connect(host=hostname, user=username, passwd=password, db=database, connect_timeout=3000)
        conn.autocommit(True)
        return conn.cursor(pymysql.cursors.DictCursor)

    def insert(self, table, data, ignore_duplicates=False):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, placeholders)
        try:
            self.cursor.execute(sql, list(data.values()))
        except pymysql.err.IntegrityError:
            if not ignore_duplicates:
                raise
