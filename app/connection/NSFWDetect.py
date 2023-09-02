import os.path

from app.connection.ImageBaseConnection import ImageBaseConnection
from app.module.nsfw import NSFWDetectorApi
from concurrent.futures import ThreadPoolExecutor


class NSFWDetect(ImageBaseConnection):
    async def connection(self):
        max_workers = self.values.get('max_workers', 5)
        self.conn = NSFWDetectorApi()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.logger.info(f"Успешное соединение: {self.conn}, {max_workers=}")
        return True

    async def classify(self, input_data):
        if isinstance(input_data, str) and not os.path.isfile(input_data):
            input_data = await self.conn.download_image(input_data)

        image_data = await self._prepare_image(input_data)

        try:
            return await self.loop.run_in_executor(self.executor, self.conn.predict, image_data)
        finally:
            os.remove(image_data)
