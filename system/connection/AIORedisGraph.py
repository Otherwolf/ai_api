from aioredisgraph import Graph  # , Node, Edge, Path
from aioredis import ConnectionError
from system.connection.BaseConnection import BaseConnection


class AIORedisGraph(BaseConnection):

    async def connection(self):
        self.redis_graph = Graph(
            self.values['base'], host=self.values.get('host', 'localhost'), port=self.values.get('port', 6379),
            user=self.values.get('user', 'default'), password=self.values.get('password', '123'))
        try:
            await self.redis_graph.execute_command('PING')
        except ConnectionError as err:
            self.logger.error(f"RedisGraph не подключен! Ошибка: {err.__class__.__name__}: {err}")
            return False
        self.logger.info(f"RedisGraph подключен (БД: {self.values['base']})")
        return True

    # Запрос в БД
    async def query(self, *args, **kwargs):
        return await self.redis_graph.query(*args, **kwargs)

    async def query_bool(self, query_txt):
        answer = await self.query(query_txt)
        return bool(answer.result_set[0][0])

    # Удаление БД графа
    async def delete(self):
        return await self.redis_graph.delete()
