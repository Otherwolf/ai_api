import orjson


def json_loads(text):
    if text:
        try:
            return orjson.loads(text)
        except orjson.JSONDecodeError:
            pass


def json_dumps(val):
    return orjson.dumps(val).decode('UTF-8')
