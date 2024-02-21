import operator
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, setcontext, Context
from typing import Callable

if not __package__:
    from words import parse, WordType, Word
else:
    from .words import parse, WordType, Word

__all__ = ["calculate"]

setcontext(Context(prec=30))

MIN = Decimal("1e-29")

DEBUG_FLAG = False

FUNCS = {"sum", "max", "min", "abs"}


@dataclass
class Operator:
    w: int
    """weight"""
    operator: str
    """operator name"""
    func: Callable | None
    """function"""
    pc: int | None = None  # parameters count None for list
    """parameter count"""


@dataclass
class Number:
    value: Decimal | None
    meta: Word


_OPER_DICT = {
    "+": Operator(10, "+", operator.add),
    "-": Operator(10, "-", operator.sub),
    "*": Operator(20, "*", operator.mul),
    "/": Operator(20, "/", operator.truediv),
    "^": Operator(30, "^", operator.pow),
    "(": Operator(100, "(", None),
    ")": Operator(-100, ")", None),
    ",": Operator(0, ",", None),
    # func's weight is same with '('
    "sum": Operator(100, "sum", sum),
    "max": Operator(100, "max", max),
    "min": Operator(100, "min", min),
    "abs": Operator(100, "abs", abs, 1),
}

_ABYSS = Operator(-10000, "", None)


class Chain(object):
    def __init__(self, raw: str, register: Callable | None = None):
        self._operators: list[Operator] = []
        self._nums: list[Decimal | None] = []
        self._register = register

        base = 0

        words = parse(raw)
        if words is None or words == []:
            raise ValueError("not valid")

        for word in words:
            match word.word_type:
                case WordType.LEFTPAREN | WordType.RIGHTPAREN:
                    base += _OPER_DICT[word.value_str].w

                case WordType.FUNCNAME:
                    if word.value_str not in FUNCS:
                        raise ValueError(f"unknown function: {word.word_str}")
                    op = deepcopy(_OPER_DICT[word.value_str])
                    op.w += base
                    self._operators.append(op)
                    self._nums.append(None)

                case WordType.OPERATOR | WordType.COMMA:
                    if word.value_str not in _OPER_DICT:
                        raise ValueError(f"unknown operator: {word.word_str}")
                    op = deepcopy(_OPER_DICT[word.value_str])
                    op.w += base
                    self._operators.append(op)

                case WordType.NUM:
                    num = Decimal(word.value_str)  # number(word)
                    if abs(num) <= MIN:
                        num = Decimal("0")
                    self._nums.append(num)

                case WordType.REGISTER:
                    if self._register is None:
                        raise ValueError(f"unknown register: {word.value_str}")

                    res = self._register(word.value_str)
                    if res is None or not isinstance(res, Decimal):
                        raise ValueError(f"unknown register: {word.value_str}")

                    num = res
                    self._nums.append(num)

                case _:
                    raise ValueError(f"unknown: {word.word_str}")

        if base != 0:
            raise ValueError("not valid")

    def __len__(self) -> int:
        return len(self._operators)

    def __getitem__(self, n) -> Operator:
        if n < 0 or n >= len(self):
            return _ABYSS
        return self._operators[n]

    def _delete(self, n: int):
        del self._operators[n]
        del self._nums[n + 1]

    def reduce_chain(self, n: int):
        op = self._operators[n]

        if op.operator == ",":
            pass

        elif op.operator in FUNCS:  # functions
            values = []
            values.append(self._nums[n + 1])
            self._delete(n)
            while (
                n < len(self._operators)
                and self._operators[n].operator == ","
                and self._operators[n].w == op.w
            ):
                values.append(self._nums[n + 1])
                self._delete(n)

            if op.pc is not None and len(values) != op.pc:
                raise ValueError(
                    f'func: "{ op.operator }" '
                    + f"expects { op.pc } parameters "
                    + f"get { len(values) }"
                )

            if op.func is not None:
                res = op.func(values) if op.pc is None else op.func(*values)
            else:
                raise TypeError("operator function can't be None")

            if abs(res) <= MIN:
                res = Decimal(0)

            self._nums[n] = res

        else:  # binary operators
            if op.func is not None:
                res = op.func(self._nums[n], self._nums[n + 1])
            else:
                raise TypeError("operator function can't be None")

            if abs(res) <= MIN:
                res = Decimal(0)

            self._nums[n] = res
            del self._operators[n]
            del self._nums[n + 1]

    def result(self) -> list[Decimal | None]:
        return self._nums


def calculate(s: str, register: Callable | None = None) -> Decimal | None:
    chain = Chain(s, register=register)
    while len(chain) != 0:
        if DEBUG_FLAG:
            print(chain.result())

        i = max(range(len(chain)), key=lambda a: chain[a].w)
        chain.reduce_chain(i)

    return chain.result()[0]


if __name__ == "__main__":
    DEBUG_FLAG = True

    raw_string = " 112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) "
    print(str(calculate(raw_string)))
    raw_string = " 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1"
    print(str(calculate(raw_string)))
