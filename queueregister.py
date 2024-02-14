from collections import deque
from typing import TypeVar, Generic
from collections.abc import Iterator

T = TypeVar("T")

DEBUG = False

NAME_STR = "abcdefghijklmnopqrstuvwxyz"
NAME_SET = set(NAME_STR)
QUEUE_LEN = len(NAME_STR)


class register_item:
    def __init__(self, keys, _dict, _type="keys"):
        self.keys = keys
        self.dict = _dict
        self.type = _type

    def _gen(self, _range):
        for i in _range:
            if abs(i) >= len(self.keys):
                i = i % len(self.keys)

            _key = self.keys[i]

            if _key not in self.dict:
                continue

            if self.type == "keys":
                yield _key
            elif self.type == "values":
                _value = self.dict[_key]
                yield _value
            elif self.type == "items":
                _value = self.dict[_key]
                yield _key, _value

    def __iter__(self):
        return self._gen(range(0, -len(self.keys), -1))

    def __reversed__(self):
        return self._gen(range(1, len(self.keys) + 1, 1))

    def __repr__(self):
        return f"register_item({ self.type })"


class QueueRegister(Generic[T]):
    def __init__(self, previous_symbol="_"):
        self._registor = dict()
        self._keys = deque(NAME_STR)
        self._PREVIOUS_SYMBOL = previous_symbol

        if not (len(previous_symbol) == 1 and type(previous_symbol) is str):
            raise ValueError("previous symbol only accept a character")

        self._top_cursor = "a"

    @property
    def PREVIOUS_SYMBOL(self):
        return self._PREVIOUS_SYMBOL

    def next_one(self):
        self._keys.rotate(-1)
        self._top_cursor = self._keys[0]

    def go_back(self):
        self._keys.rotate(1)
        self._top_cursor = self._keys[0]
        # self._registor[self._top_cursor] = None

    def __getitem__(self, key: str | int) -> None | T:
        l_key = key
        if type(key) == int:
            l_key = self._keys[key % len(self._keys)]

        return self._read(l_key)

    def __setitem__(self, key: str | int, new_value: None | T):
        l_key = key
        if type(key) == int:
            l_key = self._keys[key % len(self._keys)]

        self.write(new_value, l_key)

    def __iter__(self):
        for i in range(0, -QUEUE_LEN, -1):
            yield self[i]

    def keys(self) -> Iterator[str]:
        return register_item(self._keys, self._registor, _type="keys")

    def values(self) -> Iterator[T]:
        return register_item(self._keys, self._registor, _type="values")

    def items(self) -> Iterator[tuple[str, T]]:
        return register_item(self._keys, self._registor, _type="items")

    def _read(self, key: str) -> None | T:
        l_key = key
        if l_key == self._PREVIOUS_SYMBOL:
            l_key = self._keys[-1]

        if l_key in self._registor:
            return self._registor[l_key]
        return None

    def __contains__(self, key: str) -> bool:
        return self._contains(key)

    def _contains(self, key: str) -> bool:
        if key == self._PREVIOUS_SYMBOL:
            return True

        if key not in NAME_SET:
            # print("not in name set")
            return False

        if key not in self._registor:
            # print("not in register")
            return False

        if self._registor[key] == None:
            # print("register value is None")
            return False

        return True

    @property
    def cursor(self) -> str:
        return self._top_cursor

    def write(self, value: None | T, key: None | str = None):
        l_key = key
        if l_key is None:
            l_key = self._top_cursor
        elif key == self._PREVIOUS_SYMBOL:
            l_key = self._keys[-1]

        try:
            self._keys.index(l_key)
        except ValueError:
            raise ValueError

        if l_key in self._registor:
            self._registor[l_key] = value
        else:
            self._registor[l_key] = value


if __name__ == "__main__":
    DEBUG = True
    reg = QueueRegister[int]()
    reg.write(1111)
    reg.next_one()
    reg.write(2222)
    reg.next_one()
    reg.write(3333)
    reg.write(4444, reg.PREVIOUS_SYMBOL)

    print("a:", reg["a"])
    print("b:", reg["b"])
    print("c:", reg["c"])
    print("_:", reg["_"])

    print(reg.items())

    print("===========")

    for v in reg:
        print(v)

    print("===========")

    for v in reg:
        print(v)
