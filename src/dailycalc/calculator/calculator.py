import operator
from copy import deepcopy
import decimal
from decimal import (
    ROUND_05UP,
    ROUND_HALF_UP,
    Decimal,
    Context,
    getcontext,
    setcontext,
    localcontext,
)
from dataclasses import dataclass

if not __package__:
    from define import FUNC_SET, Operator, Number, Pt, WordType, Register
    from parserlogger import ParserLogger
    from words import parse
else:
    from .define import FUNC_SET, Operator, Number, Pt, WordType, Register
    from .parserlogger import ParserLogger
    from .words import parse

__all__ = ["calculate", "error_message", "Register", "RItem"]


MIN = Decimal("1e-29")

ROUND_PLACE: int = 10

DEBUG_FLAG = False


def _round(n1: Decimal, n2: Decimal):
    with localcontext(rounding=ROUND_HALF_UP):
        _res = round(n1, n2)  # type: ignore
    getcontext().flags[decimal.Inexact] = False
    return _res


OPER_DICT = {
    "+": Operator(10, "+", operator.add),
    "-": Operator(10, "-", operator.sub),
    "*": Operator(20, "*", getcontext().multiply),
    "/": Operator(20, "/", getcontext().divide),  # operator.truediv),
    "^": Operator(30, "^", getcontext().power),  # operator.pow),
    "(": Operator(100, "(", lambda _, b: b),
    ")": Operator(-100, ")", lambda a, _: a),
    ",": Operator(0, ",", None),
    # func's weight is same with '('
    "sum": Operator(w=100, operator="sum", func=lambda *args: sum(list(args))),
    "max": Operator(w=100, operator="max", func=lambda *args: max(list(args))),
    "min": Operator(w=100, operator="min", func=lambda *args: min(list(args))),
    "abs": Operator(w=100, operator="abs", func=abs, sig=[Pt.Num]),
    "log": Operator(
        w=100,
        operator="log",
        func=lambda x: getcontext().log10(x),
        sig=[Pt.Num],
    ),
    "ln": Operator(
        w=100, operator="ln", func=lambda x: getcontext().ln(x), sig=[Pt.Num]
    ),
    "exp": Operator(
        w=100, operator="exp", func=lambda x: getcontext().exp(x), sig=[Pt.Num]
    ),
    "sqrt": Operator(
        w=100,
        operator="sqrt",
        func=lambda x: getcontext().sqrt(x),
        sig=[Pt.Num],
    ),
    "round": Operator(
        w=100, operator="round", func=_round, sig=[Pt.Num, Pt.Int]
    ),
    "hex": Operator(
        w=100,
        operator="hex",
        func=lambda a, *_: Decimal(a),
        sig=[Pt.Int],
        ffunc=hex,
    ),
    "oct": Operator(
        w=100,
        operator="oct",
        func=lambda a, *_: Decimal(a),
        sig=[Pt.Int],
        ffunc=oct,
    ),
}

ABYSS = Operator(-10000, "", None)


parser_logger: ParserLogger

resultcontext = Context(rounding=ROUND_HALF_UP)


def valid_parameters(
    op: Operator, nums: list[Number], *, logger: ParserLogger
) -> list[Decimal | int]:
    """get valid parameters:
    if parameters not match signature raise ValueError
    """

    # check count of parameters
    l_len = len(op.sig)

    if l_len == 0:
        return [n.value for n in nums]

    if l_len > 0 and len(nums) != l_len:
        _error = f"func {op.operator}: expecting { l_len } parameters got { len(nums) }"

        if l_len > len(nums):
            l_at = nums[-1].words[-1].end
            l_to = 0
        else:
            l_at = nums[l_len].words[0].offset
            l_to = nums[-1].words[-1].end

        logger.add(_error, at=l_at, to=l_to, forced=True)
        raise ValueError(_error)

    # check and convert parameters type
    res: list[Decimal | int] = []

    for l_type, l_num in zip(op.sig, nums):
        if l_type == Pt.Num:
            res.append(l_num.value)

        if l_type == Pt.Int:
            l_int_value = round(l_num.value)
            if l_num.value != l_int_value:
                _error = f"this param must be Integer, got {l_num.value}"
                logger.add(
                    _error,
                    at=l_num.words[0].offset,
                    to=l_num.words[-1].end,
                    forced=True,
                )
                raise ValueError(_error)
            res.append(int(l_int_value))

    return res


@dataclass
class RItem:
    value: Number
    tag: str = ""


class Chain(object):
    def __init__(
        self,
        raw: str,
        *,
        register: Register[RItem] | None = None,
        logger: ParserLogger,
    ):

        self._operators: list[Operator] = []
        self._nums: list[Number] = []
        self._register = register
        self.logger = logger

        base = 0
        words = parse(raw, log=self.logger)

        if words is None or words == []:
            raise ValueError("not valid")

        self.logger.clear()

        for word in words:
            match word.type:
                case WordType.LEFTPAREN:
                    op = deepcopy(OPER_DICT[word.value_str])
                    op.words = [word]
                    op.w += base
                    self._operators.append(op)
                    self._nums.append(Number.placeholder())

                    base += OPER_DICT[word.value_str].w

                case WordType.RIGHTPAREN:
                    op = deepcopy(OPER_DICT[word.value_str])
                    op.words = [word]
                    op.w = base
                    self._operators.append(op)
                    self._nums.append(Number.placeholder())

                    base += OPER_DICT[word.value_str].w

                case WordType.FUNCNAME:
                    if word.value_str not in FUNC_SET:
                        _error = f"unknown function: {word.word_str}"
                        self.logger.add(
                            _error, at=word.offset, to=word.end, forced=True
                        )
                        raise ValueError(_error)

                    op = deepcopy(OPER_DICT[word.value_str])
                    op.w += base
                    op.words = [word]
                    self._operators.append(op)
                    self._nums.append(Number.placeholder())

                case WordType.OPERATOR | WordType.COMMA:
                    if word.value_str not in OPER_DICT:
                        _error = f"unknown operator: {word.word_str}"
                        self.logger.add(_error, at=word.offset, forced=True)
                        raise ValueError(_error)

                    op = deepcopy(OPER_DICT[word.value_str])
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
                        self.logger.add(_error, at=word.offset, forced=True)
                        raise ValueError(_error)

                    try:
                        reg_key = word.value_str.removeprefix("@")
                        res = self._register.read(reg_key)
                    except ValueError as e:
                        _error = f"{e}"
                        self.logger.add(
                            _error, at=word.offset, to=word.end, forced=True
                        )
                        raise ValueError(_error)

                    num = res.value
                    self._nums.append(Number(num.value, [word]))

                case WordType.REGISTERLIST:
                    if self._register is None:
                        _error = f"unknown register: {word.value_str}"
                        self.logger.add(_error, at=word.offset, forced=True)
                        raise ValueError(_error)

                    list_str = word.value_str.removeprefix("@")

                    try:
                        l_from, l_to = list_str.split("_")[:2]
                        res_list = self._register.read_list((l_from, l_to))
                    except ValueError as e:
                        _error = f"{e}"
                        self.logger.add(
                            _error, at=word.offset, to=word.end, forced=True
                        )
                        raise ValueError(_error)

                    for i, res in enumerate(res_list):
                        self._nums.append(Number(res.value.value, [word]))
                        if i < len(res_list) - 1:
                            self._operators.append(Operator(base, ",", None))

                case _:
                    _error = f"unknown: {word.word_str}"
                    self.logger.add(_error, at=word.offset, forced=True)
                    raise ValueError(_error)

        if base != 0:
            raise ValueError("not valid")

    def __len__(self) -> int:
        return len(self._operators)

    def __getitem__(self, n) -> Operator:
        if n < 0 or n >= len(self):
            return ABYSS
        return self._operators[n]

    def _delete(self, n: int):
        del self._operators[n]
        del self._nums[n + 1]

    def reduce_chain(self, n: int):
        op = self._operators[n]

        if op.operator == ",":
            pass

        elif op.operator in FUNC_SET:  # functions
            l_nums = []
            l_words = []
            l_nums.append(self._nums[n + 1])
            l_words.extend(op.words)
            l_words.extend(self._nums[n + 1].words)

            self._delete(n)

            # get parameters
            while (
                n < len(self._operators)
                and self._operators[n].operator in {",", "(", ")"}
                and self._operators[n].w == op.w
            ):
                l_nums.append(self._nums[n + 1])
                l_words.extend(self._operators[n].words)
                l_words.extend(self._nums[n + 1].words)
                self._delete(n)

            if op.func is None:
                _error = "operator function can't be None"
                self.logger.add(_error, at=op.words[0].offset, forced=True)
                raise ValueError(_error)

            # get valid parameters
            l_values = valid_parameters(
                op=op,
                nums=[n for n in l_nums if not n.isplaceholder],
                logger=self.logger,
            )

            # calculate
            res: Decimal = op.func(*l_values)
            res_str: str = op.ffunc(*l_values) if op.ffunc else ""

            # if abs(res) <= MIN:
            #    res = Decimal(0)

            # store the result
            self._nums[n] = Number(res, l_words, res_str)

        else:  # binary operators
            if op.func is None:
                _error = "operator function can't be None"
                self.logger.add(_error, at=op.words[0].offset, forced=True)
                raise ValueError(_error)

            l_left: Number = self._nums[n]
            l_right: Number = self._nums[n + 1]
            try:
                res = op.func(l_left.value, l_right.value)
            except decimal.DivisionByZero:
                _error = "cannot divide by Zero"
                self.logger.add(
                    _error,
                    at=l_right.words[0].offset,
                    to=l_right.words[-1].end,
                    forced=True,
                )
                raise ValueError(_error)

            l_words = l_left.words + op.words + l_right.words

            # if abs(res) <= MIN:
            #     res = Decimal(0)

            self._nums[n] = Number(res, l_words)

            self._delete(n)

    def result(self) -> list[Number]:
        return self._nums


def calculate_num(
    input: str,
    *,
    logger: ParserLogger | None = None,
    register: Register | None = None,
) -> Number | None:

    global parser_logger

    getcontext().clear_flags()

    parser_logger = logger if logger is not None else ParserLogger()

    chain = Chain(input, register=register, logger=parser_logger)
    while len(chain) != 0:
        if DEBUG_FLAG:
            print(chain.result())

        i = max(range(len(chain)), key=lambda a: chain[a].w)
        chain.reduce_chain(i)

    _result = chain.result()[0]

    _context = getcontext()
    if _context.flags[decimal.Inexact]:
        _result.value = _result.value.quantize(
            Decimal("1.0000000000"), rounding=ROUND_HALF_UP
        )
    else:
        _result.value = 0 + _result.value.normalize()

    return _result


def check_calc(input: str) -> bool:
    setcontext(
        Context(
            prec=30,
            rounding=ROUND_05UP,
            flags=[decimal.Inexact, decimal.Rounded],
            traps=[decimal.DivisionByZero],
        )
    )
    try:
        _ = calculate_num(input)
    except:
        return False
    else:
        return True


def calculate(
    input: str,
    *,
    logger: ParserLogger | None = None,
    register: Register | None = None,
) -> Decimal | None:

    setcontext(
        Context(
            prec=30,
            rounding=ROUND_05UP,
            flags=[decimal.Inexact, decimal.Rounded],
            traps=[decimal.DivisionByZero],
        )
    )

    res = calculate_num(input, logger=logger, register=register)
    return res if res is None else res.value


def error_message(raw_input: str):
    return parser_logger.message(raw_input)


if __name__ == "__main__":
    DEBUG_FLAG = True

    # raw_string = "112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) +0.0000000010001"
    # print(str(calculate(raw_string)))
    print(str(calculate("8/16")))

    # raw_string = " 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1"
    # print(str(calculate(raw_string)))
