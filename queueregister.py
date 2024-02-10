from collections import deque
from typing import TypeVar, Generic

T = TypeVar("T")

DEBUG = False

NAME_STR = "abcdefghijklmnopqrstuvwxyz"
NAME_SET = set(NAME_STR)


class QueueRegister(Generic[T]):
    def __init__(self):
        self._registor = dict()
        self._registor_name = deque(NAME_STR)

        self._top_cursor = "a"

    def goto_next(self):
        self._registor_name.rotate(-1)
        self._top_cursor = self._registor_name[0]

    def __getitem__(self, key: str) -> None | T:
        return self._read(key)

    def __setitem__(self, key: str, new_value: None | T):
        self.write(new_value, key)

    def _read(self, key: str) -> None | T:
        if key in self._registor:
            return self._registor[key]
        return None

    def contains(self, key: str) -> bool:
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

    def get_cursor(self) -> str:
        return self._top_cursor

    def write(self, value: None | T, key: None | str = None):
        l_key = key if key else self._top_cursor
        try:
            self._registor_name.index(l_key)
        except ValueError:
            raise ValueError

        if l_key in self._registor:
            self._registor[l_key] = value
        else:
            self._registor[l_key] = value


if __name__ == "__main__":
    DEBUG = True
    reg = QueueRegister()
    reg.write(1111)
    reg.next_cursor()
    reg.write(2222)
    reg.next_cursor()
    reg.write(3333)

    print(reg["a"])
    print(reg["b"])
    print(reg["c"])
