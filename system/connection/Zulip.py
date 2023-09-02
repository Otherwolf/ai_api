from datetime import datetime
import orjson
from pprint import pformat
import requests

from system.connection.BaseConnection import BaseConnection


class Zulip(BaseConnection):
    async def connection(self):
        if hook := self.values.get('hook'):
            self.hook_url = hook.get('url')
            self.hook_params = hook.get('params')
            if self.hook_url and self.hook_params:
                self.logger.info("Zulip инициализирован!")
                return True
        self.logger.info("Zulip не инициализирован! Не указан hook или он некорректный!")
        return False

    def post(self, **kwargs):
        self.logger.warning('Отправка сообщения в Zulip:')
        self.logger.error(pformat(kwargs))
        text = '\n\n'.join(f"**{key}**: {value}" for key, value in kwargs.items())
        text = f":zulip:<time:{datetime.utcnow().isoformat()}>\n\n{text}"
        data = {"attachments": [{"text": text}]}
        try:
            requests.post(self.hook_url, params=self.hook_params, data=orjson.dumps(data))  # отправка в Zulip
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as err:
            self.logger.error(f"zulip error: {err.__class__.__name__}: {err}")
