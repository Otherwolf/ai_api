import orjson
from pydantic import ValidationError


class Validator:
    @staticmethod
    def error_pydantic_convert(errors):
        errors_result = []
        for error in errors:
            error_field = '.'.join(list(map(str, error['loc'])))
            msg_list = error['msg'].split('|', maxsplit=1)
            is_my_error_field = len(msg_list) == 2
            el = {
                'error_code': error['type'],
                'error_field': (msg_list[0] if is_my_error_field and msg_list[0] else error_field).upper(),
                'error_text': msg_list[1] if is_my_error_field else error['msg'],
            }
            errors_result.append(el)
        return errors_result

    def validate_json(self, class_validate, data, return_json=False, unpack=True):
        try:
            msg_dict = orjson.loads(data) if unpack else data
            msg_obj = class_validate(**msg_dict)
            return msg_dict if return_json else msg_obj, None
        except orjson.JSONDecodeError as err:
            return None, [{'error_code': 0, 'error_field': f"{err.__class__.__name__}", 'error_text': f"{err}"}]
        except ValidationError as err:
            return None, self.error_pydantic_convert(orjson.loads(err.json()))

    def validate(self, **kwargs_decorator):
        def wrapper(fnc):
            async def func_decorated(self_worker, route, message, message_num, **kwargs_worker):
                try:
                    msg_json = message.body
                except AttributeError:
                    msg_json = message
                if class_validate_header := kwargs_decorator.get('validate_header'):
                    msg_validate, error_list = self.validate_json(class_validate_header, msg_json)
                    if not error_list:
                        return await fnc(self_worker, route, msg_validate, message_num, **kwargs_worker)
                    else:
                        self_worker.logger.error(f"Сообщение #{message_num} -> {error_list}")
                return True
            return func_decorated
        return wrapper
