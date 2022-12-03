import re
import functools
from typing import Callable, Iterable, Tuple

DEBUG_FLAG = False

FMT = "{3} {1!r} \t: {2}"

_RE_NO = re.compile("[-+]?[0-9]+(\.[0-9]+)?")

OPERATORS = tuple("- + * / ^")

INDENT_CHARACTOR = "|   "

_debug_offset = ""

_error_message = ""

_ExprFunc = Callable[[Iterable], Tuple[Iterable, Iterable]]


def debug(fmt, is_expr=False):
    def _inner(func):
        @functools.wraps(func)
        def _inner2(*args, **kwargs):
            global _debug_offset

            _debug_offset += INDENT_CHARACTOR
            offset = _debug_offset[len(INDENT_CHARACTOR) :]

            if is_expr and DEBUG_FLAG:
                print(f"{offset}func <{func.__name__}> \t<= {args[0]}")

            result = func(*args, **kwargs)

            if DEBUG_FLAG:
                indicator = "🟢"
                resultStr = " ".join(result[0])
                if not result[0]:
                    indicator = "🔴"
                    resultStr = result[0]

                print(
                    f"{offset}", fmt.format(args, resultStr, func.__name__, indicator)
                )

            _debug_offset = _debug_offset[: -len(INDENT_CHARACTOR)]

            return result

        return _inner2

    return _inner


def _all(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 expression2 ... expressionN

    INPUT:
        fns: Expression Functions
    OUTPUT:
        new expression func
    """

    def _inner(s: Iterable) -> Tuple[Iterable, Iterable]:
        res = []
        stream = s
        for fn in fns:
            res_tmp, stream = fn(stream)
            if not res_tmp:
                return [], s
            res += res_tmp

        return res, stream

    return _inner


def _any(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 | expression2 | ... | expressionN

    INPUT:
        fns: expression functions
    OUTPUT:
        new expression func
    """

    def _inner(s: Iterable) -> Tuple[Iterable, Iterable]:
        for fn in fns:
            res1, stream1 = fn(s)
            if res1:
                return res1, stream1

        return [], s

    return _inner


def _do(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 [ expression2 ... [ expressionN ]...]

    INPUT:
        fns: expression functions
    OUTPUT:
        new expression func
    """

    def _inner(s: Iterable) -> Tuple[Iterable, Iterable]:
        res, stream = [], s
        for fn in fns:
            res_tmp, stream = fn(stream)
            if not res_tmp:
                break
            res += res_tmp

        return res, stream

    return _inner


def _repeat(fn: _ExprFunc) -> _ExprFunc:
    """expression = expression*

    INPUT:
        fn: expression function
    OUTPUT:
        new expression func
    """

    def _inner(s: Iterable) -> Tuple[Iterable, Iterable]:
        res = []
        res_tmp, stream = fn(s)
        while res_tmp:
            res += res_tmp
            res_tmp, stream = fn(stream)
        return res, stream

    return _inner


def space(s: Iterable) -> Tuple[Iterable, Iterable]:
    for i, c in enumerate(s):
        if not c.isspace():
            return [], s[i:]
    return [], []


@debug(FMT)
def number(s: Iterable) -> Tuple[Iterable, Iterable]:
    global _error_message

    res, stream = space(s)

    result = _RE_NO.match(stream)

    if result is None:
        _error_message = f"expect number: {stream}"
        return res, stream

    # groups = result.groups()
    num_str = result.group()
    span = result.span()
    return [num_str], stream[span[1] :]


@debug(FMT)
def operator(s: Iterable) -> Tuple[Iterable, Iterable]:
    global _error_message

    res, stream = space(s)

    for token in OPERATORS:
        if stream and stream[: len(token)] == token:
            stream = stream[len(token) :]
            res.append(token)
            break
    else:
        _error_message = f"expecting operator: {stream}"

    return res, stream


@debug(FMT)
def left_paren(s: Iterable) -> Tuple[Iterable, Iterable]:
    global _error_message

    res, stream = space(s)
    if stream and stream[0] == "(":
        res.append("(")
        stream = stream[1:]
    else:
        _error_message = f"expect '(': {stream}"
    return res, stream


@debug(FMT)
def right_paren(s: Iterable) -> Tuple[Iterable, Iterable]:
    global _error_message

    res, stream = space(s)
    if stream and stream[0] == ")":
        res.append(")")
        stream = stream[1:]
    else:
        _error_message = f"expect ')': {stream}"
    return res, stream


@debug(FMT, is_expr=True)
def _e2(s: Iterable) -> Tuple[Iterable, Iterable]:
    """expression = number [ operator number ]*"""
    return _do(number, _repeat(_all(operator, number)))(s)


@debug(FMT, is_expr=True)
def _e1(s: Iterable) -> Tuple[Iterable, Iterable]:
    """expression = '(' expression + ')'"""
    return _all(left_paren, expr, right_paren)(s)


@debug(FMT, is_expr=True)
def expr(s: Iterable) -> Tuple[Iterable, Iterable]:
    """expression =  _e2 | _e1 [ operator expression ]"""
    # _e2 is not necessarilly, can be replaced by number
    return _do(_any(_e1, _e2), _repeat(_all(operator, expr)))(s)


def parse(s: Iterable) -> Iterable:
    result, stream = expr(s)
    _, stream = space(stream)
    if result:
        if stream and stream[0]:
            if DEBUG_FLAG:
                print("unvalid expression!")
                print(_error_message)
            return []
        else:
            if DEBUG_FLAG:
                print("success!")
            return result
    else:
        if DEBUG_FLAG:
            print("unvalid expression!")
            print(_error_message)
        return []


if __name__ == "__main__":
    DEBUG_FLAG = True
    parse("(2 + 4 * 4 --4 * 12) + 1 + ((-2 + 12)) ")
