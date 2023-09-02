from datetime import datetime
from pprint import pformat
import requests
import html

from system.connection.BaseConnection import BaseConnection
from system.const import SPECIAL_FIELDS_ALERT_MESSAGE

FIELD_EMOJI = {
    'app_name': '&#128204;',
    'env': '&#128204;',
    'action': '&#129512;',
}


class Telegram(BaseConnection):
    async def connection(self):
        self.url = f"https://api.telegram.org/bot{self.values['token_bot']}/sendMessage"
        self.chat_id = self.values['chat_id']
        self.logger.info(f"Telegram sender chat_id={self.chat_id} инициализирован!")
        return True

    def post(self, **kwargs):
        self.logger.warning(f"Отправка сообщения в Telegram (chat_id={self.chat_id}):")
        self.logger.error(pformat(kwargs))
        text = '\n\n'.join(f"{FIELD_EMOJI.get(key, '&#128478;')} <b>{key}</b>: "
                           f"{f'<code>{html.escape(value)}</code>' if key in SPECIAL_FIELDS_ALERT_MESSAGE else value}"
                           for key, value in kwargs.items())
        text = f"&#128348; <u>{datetime.now().isoformat(' ', 'seconds')}</u>\n\n{text}"
        try:
            requests.post(self.url, data={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'html',
            })  # отправка в Telegram-канал
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as err:
            self.logger.error(f"Telegram send error: {err.__class__.__name__}: {err}")
