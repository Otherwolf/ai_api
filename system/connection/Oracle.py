# Скачать instantclient_21_1
# https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html
# Вызвать команду setx PATH "%PATH%;c:\inst\instantclient_19_6"
import cx_Oracle
from time import sleep
import re

from system.connection.BaseConnection import BaseConnection


class Oracle(BaseConnection):
    async def connection(self):
        return self.connect()

    def connect(self):
        list_connect = re.findall(r'[^:/@]+', self.values['dsn'])[1:]
        self.pool = cx_Oracle.SessionPool(list_connect[0], list_connect[1],
                                          f"{list_connect[2]}:{list_connect[3]}/{list_connect[4]}",
                                          min=self.values.get('min_size', 1), max=self.values.get('max_size', 2),
                                          increment=1, encoding="UTF-8", nencoding="UTF-8")
        self.connection = self.pool.acquire()
        # self.connection = cx_Oracle.connect(list_connect[0], list_connect[1],
        #                                     f'{list_connect[2]}:{list_connect[3]}/{list_connect[4]}',
        #                                     encoding="UTF-8", nencoding="UTF-8")
        if self.connection:
            self.cursor = self.connection.cursor()
            if self.cursor:
                self.logger.info('Oracle подключен!')
                return True
        self.logger.error('Oracle не подключен!')
        return False

    def func_get_cursor(self, name, *args):  # Вызов функции Oracle cursor
        for time_sleep in (1, 3, 5):
            try:
                return self.cursor.callfunc(name, cx_Oracle.CURSOR, args)
            except (cx_Oracle.OperationalError, cx_Oracle.DatabaseError) as err:
                self.logger.error(f"{err.__class__.__name__}: {err}")
                sleep(time_sleep)
                self.connect()  # Пепеподключение к Oracle
        return self.cursor.callfunc(name, cx_Oracle.CURSOR, args)

    async def close(self):
        # Release the connection to the pool
        self.pool.release(self.connection)
        # Close the pool
        self.pool.close()

    # def func(self, name, *args):  # Вызов функции Oracle string
    #     res = self.cursor.callfunc(name, cx_Oracle.STRING, args)
    #     return res
    #
    # def func_get_clob(self, name, *args):  # Вызов функции Oracle
    #     res = self.cursor.callfunc(name, cx_Oracle.CLOB, args)
    #     if res:
    #         return str(res)
    #     return res
    #
    # def proc(self, name, *args):  # Вызов процедуры Oracle
    #     self.cursor.callproc(name, args)
