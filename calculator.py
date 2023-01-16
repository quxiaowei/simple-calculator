import operator
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Callable, Optional

if __name__ == "__main__" or not __package__:
    from words import parse
else:
    from .words import parse

DEBUG_FLAG = False


FUNCS = {"sum", "max", "min"}


@dataclass
class Operator:
    w: int
    operator: str
    func: Optional[Callable]


_dict = {
    "+": Operator(10, "+", operator.add),
    "-": Operator(10, "-", operator.sub),
    "*": Operator(20, "*", operator.mul),
    "/": Operator(20, "/", operator.truediv),
    "(": Operator(100, "(", None),
    ")": Operator(-100, ")", None),
    ",": Operator(0, ",", None),
    # func's weight is same with '('
    "sum": Operator(100, "sum", sum),
    "max": Operator(100, "max", max),
    "min": Operator(100, "min", min),
}

_abyss = Operator(-10000, "", None)


class Chain(object):
    def __init__(self, raw: str):
        self._operators: List[Operator] = []
        self._num: List[Optional[Decimal]] = []

        base = 0

        for word in parse(raw):  # raw.split():
            if word in set("()"):  # ( )
                base += _dict[word].w

            elif word in FUNCS:  # functions
                op = deepcopy(_dict[word])
                op.w += base
                self._operators.append(op)
                self._num.append(None)

            elif word in set(_dict.keys()):  # operators
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
        return self._operators[n]

    def _delete(self, n: int):
        del self._operators[n]
        del self._num[n + 1]

    def reduce_chain(self, n):
        op = self._operators[n]

        if op.operator == ",":
            pass

        elif op.operator in FUNCS:  # functions
            values = []
            values.append(self._num[n + 1])
            self._delete(n)
            while (
                n < len(self._operators)
                and self._operators[n].operator == ","
                and self._operators[n].w == op.w
            ):
                values.append(self._num[n + 1])
                self._delete(n)

            self._num[n] = op.func(values)

        else:  # binary operators
            self._num[n] = op.func(self._num[n], self._num[n + 1])
            del self._operators[n]
            del self._num[n + 1]

    def result(self) -> List[Optional[Decimal]]:
        return self._num


def calculate(s: str) -> Optional[Decimal]:
    chain = Chain(s)
    while len(chain) != 0:
        if DEBUG_FLAG:
            print(chain.result())
        i = max(range(len(chain)), key=lambda a: chain[a].w)
        chain.reduce_chain(i)

    return chain.result()[0]


if __name__ == "__main__":
    DEBUG_FLAG = True

    raw_string = " 112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) "
    raw_string = " 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1"
    print(str(calculate(raw_string)))
