from enum import Enum

ENGINE_VERSION = '1.0.0'


class MessageType(Enum):
    WEB = 'web'
    RABBITMQ = 'rabbitmq'


CHAT_NAMES = ('Bitrix24', 'Mattermost', 'Slack', 'Telegram', 'Zulip')
SPECIAL_FIELDS_ALERT_MESSAGE = ('exception', 'traceback')
