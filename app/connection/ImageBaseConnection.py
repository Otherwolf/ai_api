import random

import starlette

from system.connection.BaseConnection import BaseConnection


class ImageBaseConnection(BaseConnection):
    async def _prepare_image(self, input_data):
        if isinstance(input_data, starlette.datastructures.UploadFile):
            input_data = await self.save_image(input_data)

        return input_data

    @classmethod
    async def save_image(cls, image: starlette.datastructures.UploadFile):
        """
        :param image:
        :return:
        """
        file_name = f"{random.randint(6969, 6999)}.jpg"
        with open(file_name, 'wb') as f:
            f.write(await image.read())
        return file_name

    async def close(self):
        if hasattr(self, 'executor'):
            self.executor.shutdown()
