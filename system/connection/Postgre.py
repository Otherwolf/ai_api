import asyncpg
from datetime import datetime
import copy
from typing import List

from system.module.my_json import json_dumps
from system.connection.BaseConnection import BaseConnection


class Postgre(BaseConnection):

    async def connection(self):
        try:
            self.pool = await asyncpg.create_pool(**self.values)
            self.logger.info(f"Успешное соединение: {self.connection_name} = Postgre({self.values['dsn']})")
            return True
        except Exception as err:  # (OSError, TypeError, asyncpg.exceptions.InvalidPasswordError)
            self.logger.error(f"Ошибка соединения: {self.connection_name} = Postgre({self.values['dsn']})): {err}")
            return False

    @staticmethod
    def datetime_now():
        return datetime.now()

    # Формирование WHERE в SQL запросе по переданному словарю.
    # Пример:
    # data_if -> {"info":"OK","id>":100,"text is NULL":None }
    # Результат: ("info=$1 AND id>$2 AND text is NULL", ['OK', 100])
    @staticmethod
    def where_sql(data_if, start_i=1, delimiter=" AND "):
        i = start_i
        sql_data, values = [], []
        for field, value in data_if.items():
            sign = ''
            if isinstance(value, (tuple, set, list)):
                if not value:
                    continue
                tmp = []
                for item in value:
                    tmp.append(f"${i}")
                    values.append(item)
                    i += 1
                str_eq_value = f" IN({','.join(tmp)})"
            else:
                if field[-1] not in ('>', '<', '='):
                    sign = "="
                if value in (None, '') and field.find(' ', 1) > -1:
                    sign = ""
                    str_eq_value = ""
                else:
                    str_eq_value = f"${i}"
                    if isinstance(value, dict):
                        values.append(json_dumps(value))
                    else:
                        values.append(value)
                    i += 1
            sql_data.append(f"{field}{sign}{str_eq_value}")
        return delimiter.join(sql_data), values, i

    # UPDATE name_table
    async def update(self, name_table, set_dict, where_dict=None):
        if where_dict is None:
            where_dict = {}
        where_sql = ""
        set_dict['dt_updated'] = self.datetime_now()
        set_sql, values_sql, start_i = self.where_sql(set_dict, 1, ', ')
        if where_dict:
            where_sql, where_values, _ = self.where_sql(where_dict, start_i)
            where_sql = f" WHERE {where_sql}"
            values_sql += where_values
        sql_text = f'''
                    UPDATE {name_table} SET {set_sql}{where_sql} 
                    RETURNING id
                    '''
        async with self.pool.acquire() as conn:
            ids = await conn.fetch(sql_text, *values_sql)
            return ids

    # Обновить запись если существует, если нет, то добавить
    async def upsert(self, name_table, record, name_field_key, do_type='UPDATE'):
        if not isinstance(record, dict):
            record = {**record}
        record = copy.copy(record)
        record['dt_created'] = record['dt_updated'] = self.datetime_now()
        fields, values, values_123, i = self.values_sql(record)
        if do_type == 'UPDATE':
            del record['dt_created']
            set_sql, values_set, start_i = self.where_sql(record, i + 1, ', ')
            values += values_set
            set_txt = f" SET {set_sql}"
        else:
            set_txt = ''
        sql_text = f'''INSERT INTO {name_table}({",".join(fields)}) VALUES({",".join(values_123)})
            ON CONFLICT ({name_field_key}) DO {do_type}{set_txt} 
            RETURNING id
        '''
        async with self.pool.acquire() as conn:
            id_key = await conn.fetchval(sql_text, *values)
            return id_key

    def select_values_sql(self, name_table, where_dict=None, fields=None, end_text_sql=''):
        if where_dict is None:
            where_dict = {}
        where_sql, values_sql = '', []
        if where_dict:
            where_sql, values_sql, _ = self.where_sql(where_dict)
            where_sql = f' WHERE {where_sql}'
        if not fields:
            fields = "*"
        sql_text = f'''
           SELECT {fields} FROM {name_table}{where_sql} {end_text_sql}
           '''
        return sql_text, values_sql

    # SELECT name_table one field
    async def select(self, name_table, where_dict=None, fields=None, end_text_sql=''):
        sql_text, values_sql = self.select_values_sql(name_table, where_dict, fields, end_text_sql)
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql)

    async def select_one_field(self, name_table, where_dict=None, one_field=None, end_text_sql=''):
        sql_text, values_sql = self.select_values_sql(name_table, where_dict, one_field, end_text_sql)
        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql_text, *values_sql)

    async def select_one(self, *args, **kwargs):
        if rows := await self.select(*args, **kwargs):
            return dict(rows[0])

    @staticmethod
    def values_sql(record, start_i=0):
        fields, values, values_123, i = [], [], [], start_i
        for key, value in record.items():
            fields.append(key)
            if isinstance(value, (list, dict)):
                values.append(json_dumps(value))
            else:
                values.append(value)
            i += 1
            values_123.append(f'${i}')
        return fields, values, values_123, i

    # INSERT name_table
    async def insert(self, name_table, record):  # insert db
        record['dt_created'] = record['dt_updated'] = self.datetime_now()
        fields, values, values_123, _ = self.values_sql(record)
        sql_text = f'''
            INSERT INTO {name_table}({",".join(fields)}) VALUES({",".join(values_123)})
            RETURNING id
            '''
        async with self.pool.acquire() as conn:
            id_key = await conn.fetchval(sql_text, *values)
            # stmnt = await conn.prepare(sql_text)
            # id = await stmnt.fetchval(*values)
            return id_key  # res[0].get('id', 0)

    async def inserts(self, name_table: str, records: List[dict]):
        for record in records:
            if not record.get('dt_created'):
                record['dt_created'] = self.datetime_now()
            if not record.get('dt_updated'):
                record['dt_updated'] = self.datetime_now()
        list_values = []
        fields = values_123 = None
        for record in records:
            fields, values, values_123, _ = self.values_sql(record)
            list_values.append(values)
        if list_values and fields and values_123:
            sql_text = f'''
                        INSERT INTO {name_table}({",".join(fields)}) VALUES({",".join(values_123)})
                        '''
            async with self.pool.acquire() as conn:
                await conn.executemany(sql_text, list_values)
                return True

    # DELETE name_table
    async def delete(self, name_table, where_dict=None):
        if where_dict is None:
            where_dict = {}
        where_sql, values_sql = '', []
        if where_dict:
            where_sql, values_sql, _ = self.where_sql(where_dict)
            where_sql = f' WHERE {where_sql}'
        sql_text = f'''
           DELETE FROM {name_table}{where_sql}
           '''
        # print(f'{sql_text=} {values_sql=}')
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql)

    async def sql(self, sql_text, values_sql=None):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql_text, *values_sql) if values_sql else await conn.fetch(sql_text)

    async def close(self):
        await self.pool.close()
