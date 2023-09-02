from functools import reduce


def join_slash(a: str, b=None) -> str:
    return f"{a.rstrip('/')}/{b.lstrip('/')}" if b else a.rstrip('/')


def urljoin(*args) -> str:
    return reduce(join_slash, args) if args else ''
