from datetime import datetime
from pprint import pformat
import orjson
import requests

from system.connection.BaseConnection import BaseConnection

FIELD_EMOJI = {  # Не вынес в константы, так как в разных чатах м.б. разные иконки
    'app_name': '&#128204;',
    'env': '&#128204;',
    'action': '&#129512;',
}


class Mattermost(BaseConnection):
    async def connection(self):
        if hook_url := self.values.get('hook_url'):
            self.hook_url = hook_url
            self.logger.info("Mattermost инициализирован!")
            return True
        self.logger.info("Mattermost не инициализирован! Не указан hook или он некорректный!")
        return False

    def post(self, **kwargs):
        self.logger.warning("Отправка сообщения в Mattermost:")
        self.logger.error(pformat(kwargs))
        text = '\n\n'.join(f"{FIELD_EMOJI.get(key, '&#129534;')} **{key}**: {value}" for key, value in kwargs.items())
        text = f"&#128348; _{datetime.now().isoformat(' ', 'seconds')}_\n\n{text}"
        try:
            requests.post(url=self.hook_url, data=orjson.dumps({'text': text}))  # отправка в Mattermost-канал
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as err:
            self.logger.error(f"Mattermost send error: {err.__class__.__name__}: {err}")
