import aioredis
import orjson

from system.connection.BaseConnection import BaseConnection


class AIORedis(BaseConnection):

    async def connection(self):
        params = {key: value for key, value in self.values.items() if key not in ('host', 'port')}
        try:
            self.pool = self.r = await aioredis.create_redis_pool(f"redis://{self.values['host']}:"
                                                                  f"{self.values.get('port', 6379)}", **params)
            if self.r.ping():
                self.logger.info("Redis connected!")
                return True
            else:
                self.logger.error("Redis doesn`t ping!")
        except aioredis.ProtocolError:
            self.logger.error("Redis is not connected!")
        return False

    # Генерация ключа
    @staticmethod
    def gen_key(*args):
        return ':'.join(args)

    # Проверка на существование записи/записей
    async def exists(self, *args):
        return await self.r.exists(*args)

    # Записать каталог в Redis
    async def set_dict(self, name_field: str, data):
        d = {
            name_field: orjson.dumps(data)
        }
        await self.r.mset(d)

    # Установить данные Redis
    async def set(self, name_field: str, value):
        await self.r.set(name_field, value)

    # Получить данные из Redis
    async def get(self, name_field: str):
        return await self.r.get(name_field)

    # Добавление к значению 1
    async def incr(self, name_field: str):
        await self.r.incr(name_field)

    # Вычитание из значения 1
    async def decr(self, name_field: str):
        await self.r.decr(name_field)

    async def keys(self, pattern):
        return await self.r.keys(pattern)

    # Удаление поля или полей
    async def delete(self, *args):
        return await self.r.delete(*args)

    # Установить значение на время жизни time в секундах
    async def setex(self, name_field: str, time: int, value):
        return await self.r.setex(name_field, time, value)

    # Добавить значение в очередь
    async def lpush(self, key, value, *values):
        return await self.r.lpush(key, value, *values)

    # Добавить значение в очередь
    async def rpush(self, key, value, *values):
        return await self.r.rpush(key, value, *values)

    # Достать значение из очереди
    async def lpop(self, *args, **kwargs):
        return await self.r.lpop(*args, **kwargs)

    # Достать значение из очереди
    async def rpop(self, *args, **kwargs):
        return await self.r.rpop(*args, **kwargs)

    # Получить информацию о глубине очереди
    async def llen(self, key):
        return await self.r.llen(key)
