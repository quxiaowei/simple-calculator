import operator
import itertools
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, setcontext, Context
from typing import Callable

if not __package__:
    from words import parse, WordType, Word, ParserLog
else:
    from .words import parse, WordType, Word, ParserLog

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
    words: list[Word] = None


@dataclass
class Number:
    value: Decimal | None
    words: Word | None = None


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

parser_log: ParserLog


class Chain(object):
    def __init__(
        self,
        raw: str,
        /,
        register: Callable | None = None,
        log: ParserLog | None = None,
    ):
        global parser_log

        self._operators: list[Operator] = []
        self._nums: list[Number | None] = []
        self._register = register
        self.parser_log = log if log is not None else ParserLog()

        base = 0
        words = parse(raw, log=self.parser_log)

        if words is None or words == []:
            raise ValueError("not valid")

        self.parser_log.clear()

        for word in words:
            match word.word_type:
                case WordType.LEFTPAREN | WordType.RIGHTPAREN:
                    base += _OPER_DICT[word.value_str].w

                case WordType.FUNCNAME:
                    if word.value_str not in FUNCS:
                        _error = f"unknown function: {word.word_str}"
                        self.parser_log.add(word.offset, _error, forced=True)
                        raise ValueError(_error)

                    op = deepcopy(_OPER_DICT[word.value_str])
                    op.w += base
                    op.words = [word]
                    self._operators.append(op)
                    self._nums.append(None)

                case WordType.OPERATOR | WordType.COMMA:
                    if word.value_str not in _OPER_DICT:
                        _error = f"unknown operator: {word.word_str}"
                        self.parser_log.add(word.offset, _error, forced=True)
                        raise ValueError(_error)

                    op = deepcopy(_OPER_DICT[word.value_str])
                    op.w += base
                    op.words = [word]
                    self._operators.append(op)

                case WordType.NUM:
                    num = Decimal(word.value_str)  # number(word)
                    if abs(num) <= MIN:
                        num = Decimal("0")
                    self._nums.append(Number(num, [word]))

                case WordType.REGISTER:
                    if self._register is None:
                        _error = f"unknown register: {word.value_str}"
                        self.parser_log.add(word.offset, _error, forced=True)
                        raise ValueError(_error)
                    res = self._register(word.value_str)
                    if res is None or not isinstance(res, Decimal):
                        _error = f"unknown register: {word.value_str}"
                        self.parser_log.add(word.offset, _error, forced=True)
                        raise ValueError(_error)

                    num = res
                    self._nums.append(Number(num, [word]))

                case _:
                    _error = f"unknown: {word.word_str}"
                    self.parser_log.add(word.offset, _error, forced=True)
                    raise ValueError(_error)

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
            l_nums = []
            l_nums.append(self._nums[n + 1])

            self._delete(n)

            while (
                n < len(self._operators)
                and self._operators[n].operator == ","
                and self._operators[n].w == op.w
            ):
                l_nums.append(self._nums[n + 1])
                self._delete(n)

            if op.pc is not None and len(l_nums) != op.pc:
                _error = f'func: "{ op.operator }" expecting { op.pc } parameters got { len(l_nums) }'
                self.parser_log.add(op.words[0].offset, _error, forced=True)
                raise ValueError(_error)

            l_values = [n.value for n in l_nums]
            if op.func is not None:
                res = op.func(l_values) if op.pc is None else op.func(*l_values)
            else:
                _error = "operator function can't be None"
                self.parser_log.add(op.words[0].offset, _error, forced=True)
                raise ValueError(_error)

            if abs(res) <= MIN:
                res = Decimal(0)

            l_words = op.words + list(itertools.chain(*[n.words for n in l_nums]))
            self._nums[n] = Number(res, l_words)

        else:  # binary operators

            if op.func is None:
                _error = "operator function can't be None"
                self.parser_log.add(op.words[0].offset, _error, forced=True)
                raise ValueError(_error)

            l_left: Number = self._nums[n]
            l_right: Number = self._nums[n + 1]

            res = op.func(l_left.value, l_right.value)

            if abs(res) <= MIN:
                res = Decimal(0)

            l_words = l_left.words + op.words + l_right.words
            self._nums[n] = Number(res, l_words)

            del self._operators[n]
            del self._nums[n + 1]

    def result(self) -> list[Decimal | None]:
        return self._nums


def calculate(
    s: str, /, register: Callable | None = None, log: ParserLog | None = None
) -> Decimal | None:
    chain = Chain(s, register=register, log=log)
    while len(chain) != 0:
        if DEBUG_FLAG:
            print(chain.result())

        i = max(range(len(chain)), key=lambda a: chain[a].w)
        chain.reduce_chain(i)

    return chain.result()[0].value


if __name__ == "__main__":
    DEBUG_FLAG = True

    raw_string = (
        " 112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) "
    )
    print(str(calculate(raw_string)))
    raw_string = " 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1"
    print(str(calculate(raw_string)))
