from collections import defaultdict
import orjson
import hashlib
from typing import Union


def dict_to_hash_md5(dict_for_cache: Union[dict, list]) -> str:
    return hashlib.md5(orjson.dumps(dict_for_cache, option=orjson.OPT_SORT_KEYS)).hexdigest()


class SetDict:
    def __init__(self, *args):
        self.set_dict = {}
        self.set_dict_count = defaultdict(int)
        for el_args in args:
            for el_dict in (el_args if isinstance(el_args, (list, tuple, set)) else (el_args, )):
                self.add(el_dict)

    # Добавление элемента в set_dict
    def add(self, el_dict: dict, fl_overwrite: bool = True) -> bool:
        if not isinstance(el_dict, dict):
            return False
        el_hash = dict_to_hash_md5(el_dict)
        self.set_dict_count[el_hash] += 1
        if el_hash in self.set_dict and not fl_overwrite:
            return False
        self.set_dict[el_hash] = el_dict
        return True

    def count(self, el_dict: dict) -> int:
        el_hash = dict_to_hash_md5(el_dict)
        return self.set_dict_count[el_hash]

    def __str__(self):
        return f"{{{', '.join(str(el_dict) for el_dict in self.set_dict.values())}}}"

    def __len__(self):
        return len(self.set_dict)

    def __iter__(self):
        self.iter_keys = iter(self.set_dict.keys())
        return self

    def __next__(self):
        if key := next(self.iter_keys):
            return self.set_dict[key]

    def __getitem__(self, index: int):
        if not isinstance(index, int):
            raise TypeError("The index must be a number")
        return self.set_dict[list(self.set_dict)[index]]

    def __contains__(self, el_dict):
        el_hash = dict_to_hash_md5(el_dict)
        return el_hash in self.set_dict


if __name__ == "__main__":
    d = ({'b': 2, 'a': 1}, {'a': 1, 'b': {'a': 1, 'b': 2}}, {'b11': 2, 'a22': 1})
    set_dict = SetDict(d[0], d)
    set_dict.add(d[1])
    set_dict.add(d[2])
    for el in set_dict:
        print(set_dict.count(el), el)
    for i in range(len(set_dict)):
        print(set_dict[i])
    print(d[0] in set_dict)
