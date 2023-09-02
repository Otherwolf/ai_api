import re


# Взять содержимое тега
def get_tag_text(text, tag):
    res = re.search(f"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL)
    return res.groups()[0] if res else None


# Удаление тега из текста
def del_tag_text(text, tag, count=1):
    return re.sub(f"<{tag}>(.*?)</{tag}>", "", text, count=count, flags=re.DOTALL)
