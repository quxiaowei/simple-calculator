import re
from typing import Callable

if not __package__:
    from debug import word_debug, debug_is_on, open_debug
else:
    from .debug import word_debug, debug_is_on, open_debug

__all__ = ["number", "parse"]

FMT = "{3} {1!r} \t: {2}"

_RE_NO = re.compile("[-+]?[0-9]+(\.[0-9]+)?([Ee][-+]?[0-9]+)?")
_RE_HEX_NO = re.compile("0[Xx][0-9,a-f,A-F]+")
_RE_OCT_NO = re.compile("0[Oo][0-7]+")

OPERATORS = tuple("- + * / ^")

FUNCS = {"sum", "max", "min", "abs"}

_error_message = ""

Element = str

ElementStream = list[Element]

_ExprFunc = Callable[[str], tuple[ElementStream, str]]

if __name__ == "__main__":
    open_debug()
    pass


def _all(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 expression2 ... expressionN

    Args:
        fns: Expression Functions
    return:
        new expression func
    """

    def _inner(s: str) -> tuple[ElementStream, str]:
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

    Args:
        fns: expression functions
    return:
        new expression func
    """

    def _inner(s: str) -> tuple[ElementStream, str]:
        res, stream = [], s
        for fn in fns:
            res, stream = fn(stream)
            if res:
                return res, stream

        return res, stream

    return _inner


def _do(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 [ expression2 ... [ expressionN ]...]

    Args:
        fns: expression functions
    return:
        new expression func
    """

    def _inner(s: str) -> tuple[ElementStream, str]:
        res, stream = [], s
        for fn in fns:
            res_tmp, stream = fn(stream)
            if not res_tmp:
                break
            res += res_tmp

        return res, stream

    return _inner


def _repeat(fn: _ExprFunc, at_least_once=False) -> _ExprFunc:
    """expression = expression*

    Args:
        fn: expression function
        at_least_once: if True ( expression = expression+ )
    return:
        new expression func
    """

    def _inner(s: str) -> tuple[ElementStream, str]:
        res = []

        res_tmp, stream = fn(s)
        while res_tmp:
            res += res_tmp
            res_tmp, stream = fn(stream)

        if not res and not at_least_once:
            res.append([])

        return res, stream

    return _inner


def space(s: str) -> tuple[ElementStream, str]:
    for i, c in enumerate(s):
        if not c.isspace():
            return [], s[i:]
    return [], ""


@word_debug(FMT)
def number(s: str) -> tuple[ElementStream, str]:
    global _error_message

    res, stream = space(s)

    match stream[:2]:
        case "0x":
            result = _RE_HEX_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 16))
        case "0o":
            result = _RE_OCT_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 8))
        case _:
            result = _RE_NO.match(stream)
            if result is not None:
                num_str = result.group()

    if result is None:
        _error_message = f"expect number: {stream}"
        return res, stream

    # num_str = result.group()
    span = result.span()
    return [num_str], stream[span[1] :]


@word_debug(FMT)
def operator(s: str) -> tuple[ElementStream, str]:
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


def _notation(note: str, drop=False) -> _ExprFunc:
    def _inner(s: str) -> tuple[ElementStream, str]:
        global _error_message

        l_note = note.strip()

        res, stream = space(s)
        if stream and stream[: len(l_note)] == note:
            if drop:
                res.append([])
            else:
                res.append(l_note)
            stream = stream[len(l_note) :]
        else:
            _error_message = f"expect '{l_note}': {stream}"

        return res, stream

    return _inner


@word_debug(FMT)
def fn_name(s: str) -> tuple[ElementStream, str]:
    RE_FN = re.compile("([\w]+)\s*\(")

    res, stream = space(s)

    result = RE_FN.match(stream)
    if result is None:
        return res, stream

    func_name = result.groups()[0]
    if not func_name in FUNCS:
        return res, stream

    return [str(func_name)], stream[len(func_name) :]


@word_debug(FMT)
def left_paren(s: str) -> tuple[ElementStream, str]:
    return _notation("(")(s)


@word_debug(FMT)
def right_paren(s: str) -> tuple[ElementStream, str]:
    return _notation(")")(s)


@word_debug(FMT)
def comma(s: str) -> tuple[ElementStream, str]:
    return _notation(",")(s)


@word_debug(FMT)
def trailing_comma(s: str) -> tuple[ElementStream, str]:
    return _notation(",", drop=True)(s)


@word_debug(FMT, is_expr=True)
def e_2(s: str) -> tuple[ElementStream, str]:
    """expression = number [ operator number ]*"""
    return _do(number, _repeat(_all(operator, number)))(s)


@word_debug(FMT, is_expr=True)
def e_1(s: str) -> tuple[ElementStream, str]:
    """expression = '(' expression ')'"""
    return _all(left_paren, expr, right_paren)(s)


@word_debug(FMT, is_expr=True)
def e_fn(s: str) -> tuple[ElementStream, str]:
    """expression = fn( expression1 [ , expression2 ]* [,]  )"""
    return _all(
        fn_name,
        left_paren,
        _do(expr, _repeat(_all(comma, expr)), trailing_comma),
        right_paren,
    )(s)


@word_debug(FMT, is_expr=True)
def expr(s: str) -> tuple[ElementStream, str]:
    """expression =  _e2 | _e1 [ operator expression ]*"""
    # _e2 is not necessary, can be replaced by number
    return _do(_any(e_1, e_2, e_fn), _repeat(_all(operator, expr)))(s)


def parse(s: str) -> ElementStream:
    result, stream = expr(s)
    result = [item for item in result if item]
    _, stream = space(stream)
    if not result:
        if debug_is_on():
            print("unvalid expression!")
            print(_error_message)

        raise ValueError("unvalid expression")

    if stream and len(stream) > 0:
        if debug_is_on():
            print("unvalid expression!")
            print(_error_message)

        raise ValueError(f'can\'t understand "{ stream }"')

    if debug_is_on():
        print("success!")
    return result


def format(s: str) -> str:
    str_list = parse(s)
    print(str_list)
    if not str_list:
        return ""

    return " ".join(str_list)


if __name__ == "__main__":
    # open_debug()
    # parse("(2 + 4 * 4 --4 * 12) + 1 + ((-2 + 12)) ")
    # parse(" 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1")
    format(" 2 + ( 2 * sum (1, max(2, 3), 4, 5 )) - 1")
    # parse("max(1)")
    # parse("max(1,)")
    # parse("max(1, 2,)")
    # parse(
    #     " 2 + ( 2 * sum (1, max(2, (3), ), sum(1,1+1+1), min((5), 6, 7, 8 ))) - 1"
    # )
    # parse("  234  ")
