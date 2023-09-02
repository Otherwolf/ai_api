import redis
import orjson

from system.connection.BaseConnection import BaseConnection


class Redis(BaseConnection):

    async def connection(self):
        try:
            self.pool = redis.ConnectionPool(**self.values)
            self.r = redis.Redis(connection_pool=self.pool)
            if self.r.ping():
                self.logger.info("Redis подключен!")
                return True
            else:
                self.logger.error("Redis не пингуется!")
        except redis.ConnectionError:
            self.logger.error("Redis не подключен!")
        return False

    # Генерация ключа
    @staticmethod
    def gen_key(*args):
        return ':'.join(args)

    # Проверка на существование записи/записей
    def exists(self, *args):
        return self.r.exists(*args)

    # Записать каталог в Redis
    def set_dict(self, name_field: str, data):
        d = {
            name_field: orjson.dumps(data)
        }
        self.r.mset(d)

    # Установить данные Redis
    def set(self, name_field: str, value):
        self.r.set(name_field, value)

    # Получить данные из Redis
    def get(self, name_field: str):
        return self.r.get(name_field)

    # Удаление поля или полей
    def delete(self, *args):
        return self.r.delete(*args)

    # Установить значение на время жизни time в секундах
    def setex(self, name_field: str, time: int, value):
        return self.r.setex(name_field, time, value)

    # Добавить значение в очередь
    def lpush(self, key, *values):
        return self.r.lpush(key, *values)

    # Добавить значение в очередь
    def rpush(self, key, *values):
        return self.r.rpush(key, *values)

    # Достать значение из очереди
    def lpop(self, name):
        return self.r.lpop(name)

    # Достать значение из очереди
    def rpop(self, name):
        return self.r.rpop(name)

    # Получить информацию о глубине очереди
    def llen(self, key):
        return self.r.llen(key)

    # Добавить единицу к значению по ключу
    def incr(self, key, amount=1):
        return self.r.incr(key, amount)
