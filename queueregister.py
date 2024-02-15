from collections import deque
from typing import TypeVar, Generic, Optional
from collections.abc import Iterator, Iterable, Generator, Reversible

__all__ = ["QueueRegister"]

T = TypeVar("T")

DEBUG = False

NAME_STR = "abcdefghijklmnopqrstuvwxyz"
NAME_SET = set(NAME_STR)
QUEUE_LEN = len(NAME_STR)


class register_item(Generic[T]):
    """
    reversible iterator for register
    """

    def __init__(self, keys: Iterable[str], _dict: dict[str, T], _type="keys"):
        """
        Args:
            keys: key collection
            _dict: dictionary
            _type: "keys", "values", "items" determine which view it would iterate
        """
        self.keys = keys
        self.dict = _dict
        self.type = _type

    def _gen(self, _range: Iterable[int]) -> Generator:
        """
        generator of register
        """
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

    def __len__(self) -> int:
        count = 0
        for key in self.keys:
            if key in self.dict and self.dict[key] is not None:
                count += 1
        return count

    def __iter__(self) -> Iterator:
        return self._gen(range(0, -len(self.keys), -1))

    def __reversed__(self) -> Iterator:
        return self._gen(range(1, len(self.keys) + 1, 1))

    def __repr__(self) -> str:
        return f"register_item({ self.type })"


class QueueRegister(Generic[T]):
    """
    a loop dict-like structure with keys a-z, iterable, subscriptable.\n
    support KeysView, ValuesView, ItemsView
    """

    def __init__(self, previous_symbol: str = "_"):
        self._registor: dict[str, T] = dict()
        self._keys = deque(NAME_STR)
        self._PREVIOUS_SYMBOL = previous_symbol

        if not (len(previous_symbol) == 1 and type(previous_symbol) is str):
            raise ValueError("previous symbol only accept a character")

        self._top_cursor = "a"

    @property
    def PREVIOUS_SYMBOL(self) -> str:
        return self._PREVIOUS_SYMBOL

    def next_one(self):
        """
        rotate registor to next one
        """
        self._keys.rotate(-1)
        self._top_cursor = self._keys[0]

    def go_back(self):
        """
        rotate registor back by one
        """
        self._keys.rotate(1)
        self._top_cursor = self._keys[0]
        # self._registor[self._top_cursor] = None

    def __getitem__(self, key: str | int) -> Optional[T]:
        """
        read value by key or index
        """
        l_key = key
        if type(key) == int:
            l_key = self._keys[key % len(self._keys)]

        return self._read(l_key)

    def __setitem__(self, key: str | int, new_value: Optional[T]):
        """
        set value by key or index
        """
        l_key = key
        if type(key) == int:
            l_key = self._keys[key % len(self._keys)]

        self.write(new_value, l_key)

    def __iter__(self) -> Generator[T]:
        for i in range(0, -QUEUE_LEN, -1):
            yield self[i]

    def __len__(self) -> int:
        count = 0
        for key in self._keys:
            if key in self._registor and self._registor[key] is not None:
                count += 1
        return count

    def keys(self) -> Iterator[str]:
        """
        get KeysView
        """
        return register_item(self._keys, self._registor, _type="keys")

    def values(self) -> Iterator[T]:
        """
        get ValuesView
        """
        return register_item(self._keys, self._registor, _type="values")

    def items(self) -> Iterator[tuple[str, T]]:
        """
        get ItemsView
        """
        return register_item(self._keys, self._registor, _type="items")

    def _read(self, key: str) -> Optional[T]:
        """
        read value by key or index
        """
        l_key = key
        if l_key == self._PREVIOUS_SYMBOL:
            l_key = self._keys[-1]

        if l_key in self._registor:
            return self._registor[l_key]
        return None

    def __contains__(self, key: str) -> bool:
        """
        whether register contains key
        """
        return self._contains(key)

    def _contains(self, key: str) -> bool:
        """
        whether register contains key
        """
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

    def write(self, value: Optional[T], key: Optional[str] = None):
        """
        set value by key

        Args:
            key: default value is None, then write to cursor position
        """

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
