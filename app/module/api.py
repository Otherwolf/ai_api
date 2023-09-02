import random
import string
import aiohttp
import starlette


class Api:
    MAX_IMAGE_SIZE = 5 * 1000000
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/112.0.0.0 YaBrowser/23.5.3.904 Yowser/2.5 Safari/537.36'

    @classmethod
    def _get_session(cls) -> aiohttp.ClientSession:
        new_session = aiohttp.ClientSession()
        new_session.headers['User-Agent'] = cls.user_agent
        return new_session

    @staticmethod
    def _get_str_kwargs(**kwargs) -> str:
        """
        словарь превращаем в строку формата url 'name=value&name2=value2'
        :param kwargs:
        :return:
        """
        return '&'.join([f'{key}={value}' for key, value in kwargs.items()])

    @staticmethod
    def _generate_boundary() -> str:
        boundary = '----WebKitFormBoundary' \
                   + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        return boundary

    @classmethod
    async def download_image(cls, url):
        """
        Не забудь удалить файл после использования
        :param url:
        :return:
        """
        file_name = f"{random.randint(6969, 6999)}.jpg"
        async with cls._get_session() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                if int(response.headers['Content-Length']) > cls.MAX_IMAGE_SIZE:
                    return False
                with open(file_name, 'wb') as f:
                    f.write(await response.read())
        return file_name
