import os
from concurrent.futures import ThreadPoolExecutor

from app.connection.BaseConnection import BaseConnection
from app.module.aesthetics.api import AestheticsScorerApi


class Aesthetics(BaseConnection):
    async def connection(self):
        max_workers = self.values.get('max_workers', 5)
        device = self.values.get('device')

        self.conn = AestheticsScorerApi(device)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.logger.info(f"Connection is successful: {self.conn}, {max_workers=}")
        return True

    async def classify(self, input_data):
        if isinstance(input_data, str) and not os.path.isfile(input_data):
            input_data = await self.conn.download_image(input_data)

        input_data = await self._prepare_image(input_data)
        try:
            return await self.loop.run_in_executor(self.executor, self.conn.predict, input_data)
        finally:
            os.remove(input_data)
