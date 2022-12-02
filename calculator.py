import operator
from copy import deepcopy
from decimal import Decimal
from typing import List, Callable, Optional

from words import parse

DEBUG_FLAG = False


class Operator:
    def __init__(self, w: int, oper: str, func: Optional[Callable]):
        self.w = w
        self.operator = oper
        self.func = func


_dict = {
    "+": Operator(2, "+", operator.add),
    "-": Operator(2, "-", operator.sub),
    "*": Operator(4, "*", operator.mul),
    "/": Operator(4, "/", operator.truediv),
    "(": Operator(5, "(", None),
    ")": Operator(-5, ")", None),
}

_abyss = Operator(-10000, "", None)


class Chain(object):
    def __init__(self, raw: str):
        self._operators: List[Operator] = []
        self._num: List[Decimal] = []

        base = 0

        for word in parse(raw):  # raw.split():
            if word in set(_dict.keys()):
                if word in set("()"):
                    base += _dict[word].w
                else:
                    op = deepcopy(_dict[word])
                    op.w += base
                    self._operators.append(op)
            else:
                num = Decimal(word)  # number(word)
                self._num.append(num)

        if base != 0:
            pass  # error

    def __len__(self):
        return len(self._operators)

    def __getitem__(self, n) -> Operator:
        if n < 0 or n >= len(self):
            return _abyss
        else:
            return self._operators[n]

    def reduce_chain(self, n):
        self._num[n] = self._operators[n].func(self._num[n], self._num[n + 1])
        del self._operators[n]
        del self._num[n + 1]

    def result(self) -> List[Decimal]:
        return self._num


def calculate(s: str) -> Decimal:
    chain = Chain(s)
    while len(chain) != 0:
        if DEBUG_FLAG:
            print(chain.result())
        j = max(range(len(chain)), key=lambda a: chain[a].w)
        chain.reduce_chain(j)

    return chain.result()[0]


if __name__ == "__main__":
    DEBUG_FLAG = True

    raw_string = (
        "112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 )"
    )
    print(str(calculate(raw_string)))
