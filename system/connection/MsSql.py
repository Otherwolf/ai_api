import pyodbc

from system.connection.BaseConnection import BaseConnection
from system.module.xml_to_dict import in_list


class MsSql(BaseConnection):
    async def connection(self):
        dsn_no_psw = f"DRIVER={pyodbc.drivers()[0]};SERVER={self.values['server']};" \
                     f"DATABASE={self.values['database']};UID={self.values['uid']};"
        try:
            self.conn = pyodbc.connect(f"{dsn_no_psw}PWD={self.values['pwd']};")
            self.logger.info(f"Успешное соединение: {self.conn} = MSSQL({dsn_no_psw})")
            return True
        except Exception as err:
            self.logger.error(f"Ошибка соединения: {self.connection_name} = MSSQL({dsn_no_psw}): {err}")
            return False

    async def sql(self, sql_text, fetch_type=None, params=None):
        with self.conn.cursor() as cursor:
            # print(f"{sql_text=}, {params=}")
            if params:
                cursor.execute(sql_text, in_list(params))
            else:
                cursor.execute(sql_text)
            if not sql_text.strip().upper().startswith('SELECT'):  # фиксируем в БД изменения
                self.conn.commit()
            if fetch_type == 'val':
                return cursor.fetchval()
            elif fetch_type == 'one':
                return cursor.fetchone()
            elif fetch_type == 'all':
                return cursor.fetchall()

    async def close(self):
        self.conn.close()
