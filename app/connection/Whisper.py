from app.module.whisper_jax.api import WhisperApi
from concurrent.futures import ThreadPoolExecutor

from system.connection.BaseConnection import BaseConnection


class Whisper(BaseConnection):
    async def connection(self):
        max_workers = self.values.get('max_workers', 5)
        self.conn = WhisperApi()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.logger.info(f"Успешное соединение: {self.conn}, {max_workers=}")
        return True

    async def recognize(self, input_data, language):
        return await self.loop.run_in_executor(self.executor, self.conn.recognize, input_data, language)

    async def close(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown()
