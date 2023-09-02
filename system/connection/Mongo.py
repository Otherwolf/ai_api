import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from system.connection.BaseConnection import BaseConnection


class Mongo(BaseConnection):

    async def connection(self):
        self.pool = AsyncIOMotorClient(self.values['dsn'])
        try:
            await self.pool.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            self.logger.error('Не удалось подключиться к MongoDB')
            return False
        self.logger.info('Подключение к MongoDB...')
        if indexes := self.values.get('indexes'):  # Indexes
            self.logger.info('Создание Mongo индексов...')
            await self.create_indexes(indexes)
        return True

    async def create_indexes(self, indexes):
        for db_name, index_root in indexes.items():
            self.logger.info(f'Создание индексов для БД: {db_name}')
            for collection_name, indexes_all in index_root.items():
                self.logger.info(f'Создание индекса для коллекции: {db_name}->{collection_name}')
                db = getattr(self.pool, db_name)
                collection = getattr(db, collection_name)
                for index_name, index_cfg in indexes_all.items():
                    indexes = []
                    self.logger.info(f'Создание индекса [{db_name}->{collection_name}] {index_name}: {index_cfg}')
                    for index_field, direction in index_cfg.items():
                        indexes.append((index_field, getattr(pymongo, direction)))
                    _ = await collection.create_index(indexes, name=index_name)

    async def close(self):
        self.logger.warning('Завершение mongodb pool...')
        await self.pool.close()
