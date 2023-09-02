from pprint import pformat
from slacker import IncomingWebhook

from system.connection.BaseConnection import BaseConnection
from system.const import SPECIAL_FIELDS_ALERT_MESSAGE


class Slack(BaseConnection):
    async def connection(self):
        if hook := self.values.get('hook'):
            self.hook = IncomingWebhook(hook)
            self.logger.info("Slack инициализирован!")
            return True
        else:
            self.logger.info("Slack не инициализирован! Не указан hook!")
            return False

    def post(self, **kwargs):
        self.logger.warning('Отправка сообщения в Slack:')
        self.logger.error(pformat(kwargs))
        self.hook.post(self.gen_msg(**kwargs))  # отправка в Slack

    @staticmethod
    def gen_section(fields_dict):
        if fields_dict and isinstance(fields_dict, dict):
            fields = []
            for name, value in fields_dict.items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{name.capitalize()}*\n{value}",
                })
            if len(fields) == 1:
                fields = fields[0]
                name_fields = "text"
            else:
                name_fields = "fields"
            return {
                "type": "section",
                name_fields: fields,
            }

    def gen_msg(self, **kwargs):
        fields = [{}, {}]
        for name, value in kwargs.items():
            if value:
                if name not in SPECIAL_FIELDS_ALERT_MESSAGE:
                    fields[0][name] = value
                else:
                    fields[1][name] = value
        sections = []
        for el in fields:
            section = self.gen_section(el)
            if section:
                sections.append(section)
        return {
            "blocks": [
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Clear warning"
                            },
                            "style": "primary",
                            "value": "clear_warn"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Panic!"
                            },
                            "style": "danger",
                            "value": "send_sms"

                        }
                    ]
                },
                *sections
            ]
        }
