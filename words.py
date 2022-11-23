import re
import functools
from decimal import Decimal
from typing import Iterable, Optional, Tuple, TypeVar

DEBUG_FLAG = False

FMT = "{3} {1!r} \t: {2}"

RE_NO = re.compile("[-+]?[0-9]+(\.[0-9]+)?")

OPERATORS = tuple("- + * / ^")

_debug_offset = ""


def debug(fmt, isExpr=False):
    def _inner(func):
        @functools.wraps(func)
        def _inner2(*args, **kwargs):
            global _debug_offset
            indent_charator = "|   "
            _debug_offset += indent_charator
            offset = _debug_offset[len(indent_charator):]

            if isExpr and DEBUG_FLAG:
                print(f"{offset}func <{func.__name__}> \t<= {args}")

            result = func(*args, **kwargs)

            if DEBUG_FLAG:
                indicator = "🟢"
                if not result[0]:
                    indicator = "🔴"

                print(
                    f"{offset}", fmt.format(args, result[0], func.__name__, indicator)
                )

            _debug_offset = _debug_offset[: -len(indent_charator)]

            return result

        return _inner2

    return _inner


def space(s: Iterable) -> Tuple[Optional[str], Iterable]:
    for i, c in enumerate(s):
        if not c.isspace():
            return [], s[i:]
    return [], []


@debug(FMT)
def number(s: Iterable) -> Tuple[Iterable, Iterable]:
    res, stream = space(s)

    result = RE_NO.match(stream)

    if result is None:
        return res, stream

    groups = result.groups()
    num_str = result.group()
    span = result.span()
    if groups[0]:
        return [num_str], stream[span[1] :]
    else:
        return [num_str], stream[span[1] :]


@debug(FMT)
def operator(s: Iterable) -> Tuple[Iterable, Iterable]:
    res, stream = space(s)

    for token in OPERATORS:
        if stream and stream[: len(token)] == token:
            stream = stream[len(token) :]
            res.append(token)
            break

    return res, stream


@debug(FMT)
def left_paren(s: Iterable) -> Tuple[Iterable, Iterable]:
    res, stream = space(s)
    if stream and stream[0] == "(":
        res.append("(")
        stream = stream[1:]
    return res, stream


@debug(FMT)
def right_paren(s: Iterable) -> Tuple[Iterable, Iterable]:
    res, stream = space(s)
    if stream and stream[0] == ")":
        res.append(")")
        stream = stream[1:]
    return res, stream


@debug(FMT, isExpr=True)
def _e2(s: Iterable) -> Tuple[Optional[Iterable], Iterable]:
    """
    expression = number [oper number]*
    _e2 is not necessarily
    """
    res = []

    d1, stream = number(s)
    if not d1:
        return [], s
    res += d1

    while stream:
        res1 = []
        op, s1 = operator(stream)
        if not op:
            break
        res1 += op

        n1, s2 = number(s1)
        if not n1:
            break
        res1 += n1

        stream = s2
        res += res1

    return res, stream


@debug(FMT, isExpr=True)
def _e1(s: Iterable) -> Tuple[Optional[bool], Iterable]:
    """expression = ( expression )"""
    res, stream = left_paren(s)
    if not res:
        return [], s

    res1, stream = expr(stream)
    if not res1:
        return [], s
    res += res1

    res2, stream = right_paren(stream)
    if not res2:
        return [], s
    res += res2

    return res, stream


@debug(FMT, isExpr=True)
def expr(s: Iterable) -> Tuple[Optional[bool], Iterable]:
    res, stream = _e2(s)  
    # _e2 is not necessarilly, can be replaced by number
    # res, stream = number(s)
    if not res:
        res, stream = _e1(stream)
        if not res:
            return [], stream

    while stream:
        res1, s1 = operator(stream)
        if not res1:
            break

        ep, s2 = expr(s1)
        if not ep:
            break
        res1 += ep

        stream = s2
        res += res1

    return res, stream


def parse(s: Iterable) -> bool:
    result, stream = expr(s)
    _, stream = space(stream)
    if result:
        if stream and stream[0]:
            print(f"unexpected '{stream[0]}'")
            return []
        else:
            print("success!")
            return result
    else:
        print("unvalid expression!")
        return []


if __name__ == "__main__":
    DEBUG_FLAG = True
    # number(str("  123  "))
    # number(str('  123. '))
    # number(str('  123.012 '))
    # number(str(' - 123'))
    # number(str('  - 123.012'))
    # number(str(' +  123'))
    # number(str(' + 123.012'))
    # number(str(" - 0.012"))

    # parse(' -1.1 + (+11) ')
    # parse(" ( -1.1 )  ")
    # parse(' -1.1 + 1.1 + 4.5 ')
    # parse('((( 1.1 + -1.01 ))')
    # parse("1 + (( 1.1 + -1.01 ))")
    # parse("2 + 4 * 4 -4 * 12")
    # parse("(2 + 4 * 4 -4 * 12) + 1 -2 ")
    parse("(2 + 4 * 4 -4 * 12) + 1 + (-2 + 12) ")
    # parse('((( 1.1 + + -1.01 ))')
    # parse('((( 1.1 + -s1.01 ))')
    # parse('((( 1.1. + -1.01 ))')
    # parse(" -1.1-(343-34)+(1.1+-1.1)")
