from collections import defaultdict
from typing import Optional


class RabbitErrors:
    def __init__(self, error_list=None):
        self.clear_message()
        if error_list and isinstance(error_list, list):
            for error in error_list:
                self.add_message(error['error_code'], error['error_field'], error.get('error_text'))

    def clear_message(self):
        self.errors = defaultdict(dict)

    def add_message(self, code: str, field: str, message: Optional[str] = None):
        self.errors[code].setdefault(str(field) if field else None, set()).add(message)
        # self.errors[code].add(str(message))

    def get(self):
        errors = []
        for code, field_messages in self.errors.items():
            for field, messages in field_messages.items():
                error = {
                    'error_code': code,
                    'error_field': field,
                }
                if error_text := ', '.join(message for message in messages if message and isinstance(message, str)):
                    error['error_text'] = error_text
                errors.append(error)
        return errors
        # return [{'error_code': code, 'error_field': ', '.join(message)} for code, message in self.errors.items()]

    def is_empty(self):
        return not self.errors


if __name__ == "__main__":
    rabbit_error = RabbitErrors()
    print(rabbit_error.is_empty())
    rabbit_error.add_message('test1', 'aaa1')
    rabbit_error.add_message('test1', 'aaa', 'msg_02')
    rabbit_error.add_message('test1', 'aaa', 'msg2')
    print(rabbit_error.is_empty())
    print(rabbit_error.get())
