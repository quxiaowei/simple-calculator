import re
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from typing import Callable

if not __package__:
    from debug import word_debug, debug_is_on, open_debug
else:
    from .debug import word_debug, debug_is_on, open_debug

__all__ = ["number", "parse", "ParserLog", "format"]


### classes and types


class WordType(Enum):
    NUM = 1
    OPERATOR = 2
    FUNCNAME = 3
    NOTATION = 4
    COMMA = 5
    LEFTPAREN = 6
    RIGHTPAREN = 7
    REGISTER = 8
    PLACEHOLDER = 9


@dataclass
class Word:
    word_str: str
    value_str: str
    word_type: WordType
    offset: int = 0


class ParserLog(dict[int, tuple[str, int]]):
    def add(self, key: int, message: str, /, forced=False):
        # _RE_MESSAGE = re.compile(r"\s*expecting\s+(\w+|(\'\S+\'))(, got)?")
        
        if not forced and key in self and self[key]:
            # l_old = self[key].strip()
            # l_new = message.strip()

            # if not (l_old.startswith("expecting") and l_new.startswith("expecting")):
            #     return

            # l_old_1 = l_old.split(", got")[0].removeprefix("expecting").strip()
            # l_new_1 = l_new.split(", got")[0].removeprefix("expecting").strip()

            # l_list = l_old_1.split(" or ") + [l_new_1]
            # l_list = sorted(list(set(l_list)), reverse=True)

            # self[key] = "expecting " + " or ".join(l_list)

            pass
        else:
            self[key] = (message, 0)

    def get(self) -> tuple[int, str]:
        i = max(list(self.keys()))
        return i, self[i][0]

    def message(self, s: str) -> str:
        l_buffer = list("-" * (len(s) + 4))
        l_pos, l_log = self.get()
        l_buffer[l_pos] = "^"

        l_m1 = "  Input: " + s
        l_m2 = "         " + "".join(l_buffer)
        l_m3 = "  Error: " + l_log
        return "\n".join([l_m1, l_m2, l_m3])


Element = Word

ElementStream = list[Element]

_ExprFunc = Callable[[str], tuple[ElementStream, str]]


### constants

FMT = "{3} {1!r} \t: {2}"

# _RE_NO = re.compile(r"[-+]?[0-9]+(,[0-9]{3})*(\.[0-9]+)?([Ee][-+]?[0-9]+)?")
_RE_NO = re.compile(r"[-+]?[0-9]+(\.[0-9]+)?([Ee][-+]?[0-9]+)?\b")
_RE_HEX_NO = re.compile(r"0[Xx][0-9a-fA-F]+\b")
_RE_OCT_NO = re.compile(r"0[Oo][0-7]+\b")
_RE_REGISTER = re.compile(r"\@[@a-z0-9]+\b")

OPERATORS = tuple("- + * / ^")

FUNCS = {"sum", "max", "min", "abs"}

_GUESS = False


### init

if __name__ == "__main__":
    # open_debug()
    pass


parser_log: ParserLog

g_offset: int

g_layers: int

class Stacker:
    def __init__(self):
        return self

    def __enter__(self):
        global g_layers
        g_layers += 1
        return

    def __exit__(self):
        global g_layers
        g_layers -= 1

    def layer(self)->int:
        return g_layers


def placeholder() -> Word:
    """True but empty placeholder"""
    return Word("PH", "PH", WordType.PLACEHOLDER)


def _all(*fns: _ExprFunc) -> _ExprFunc:
    """expression = expression1 expression2 ... expressionN

    Args:
        fns: Expression Functions
    return:
        new expression func
    """

    def _inner(s: str) -> tuple[ElementStream, str]:
        global g_offset
        l_offset = g_offset

        res, stream = [], s
        for fn in fns:
            res_tmp, stream = fn(stream)
            if not res_tmp:
                g_offset = l_offset
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
        global g_offset
        l_offset = g_offset

        res, stream = [], s
        for fn in fns:
            res, stream = fn(stream)
            if res:
                return res, stream

            g_offset = l_offset
            res, stream = [], s

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
        global g_offset
        l_offset = g_offset

        res, stream = [], s
        for fn in fns:
            _stream = stream
            res_tmp, stream = fn(stream)
            if not res_tmp:
                stream = _stream
                g_offset = l_offset
                break

            l_offset = g_offset
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
        global g_offset
        l_offset = g_offset

        res, stream = [], s

        _stream = stream

        res_tmp, stream = fn(stream)
        while res_tmp:
            l_offset = g_offset
            _stream = stream

            res += res_tmp
            res_tmp, stream = fn(stream)

        stream = _stream

        g_offset = l_offset

        if not res:
            res, stream = [], s

        if not res and not at_least_once:
            res, stream = [placeholder()], s

        return res, stream

    return _inner


def space(s: str) -> tuple[ElementStream, str]:
    global g_offset
    l_offset = g_offset

    for i, c in enumerate(s):
        if not c.isspace():
            return [], s[i:]
        g_offset += 1
    return [], ""


@word_debug(FMT)
def number(s: str) -> tuple[ElementStream, str]:
    global _error_message, g_offset

    res, stream = space(s)
    l_offset = g_offset

    match list(stream[:2].lower()):
        case ["0", "x"]:
            result = _RE_HEX_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 16)).lower()
                word = Word(result.group(), num_str, WordType.NUM, l_offset)
        case ["0", "o"]:
            result = _RE_OCT_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 8)).lower()
                word = Word(result.group(), num_str, WordType.NUM, l_offset)
        case ["@", _]:
            result = _RE_REGISTER.match(stream)
            if result is not None:
                num_str = result.group().lower()
                word = Word(result.group(), num_str, WordType.REGISTER, l_offset)
        case _:
            result = _RE_NO.match(stream)
            if result is not None:
                num_str = result.group().lower()
                # num_str = num_str.replace(",", "")
                word = Word(result.group(), num_str, WordType.NUM, l_offset)

    if result is None:
        g_offset = l_offset
        _error_message = f"expecting number"
        parser_log.add(g_offset, _error_message)
        return res, stream

    # num_str = result.group()
    span = result.span()
    g_offset += span[1]
    return [word], stream[span[1] :]


@word_debug(FMT)
def operator(s: str) -> tuple[ElementStream, str]:
    global _error_message, g_offset

    res, stream = space(s)
    l_offset = g_offset

    for token in OPERATORS:
        if stream and stream[: len(token)] == token:
            stream = stream[len(token) :]
            word = Word(token, token, WordType.OPERATOR, l_offset)
            res.append(word)
            g_offset += len(token)
            break
    else:
        g_offset = l_offset
        _error_message = f"expecting operator"
        parser_log.add(g_offset, _error_message)

    return res, stream


def _notation(note: str, /, drop=False, forced=False) -> _ExprFunc:
    def _inner(s: str) -> tuple[ElementStream, str]:
        global _error_message, g_offset

        l_note = note.strip()

        res, stream = space(s)
        l_offset = g_offset

        if stream and stream[: len(l_note)] == l_note:
            g_offset += len(l_note)
            if drop:
                res.append(placeholder())
                pass
            else:
                word = Word(note, note, WordType.NOTATION, l_offset)
                res.append(word)

            stream = stream[len(l_note) :]
        else:
            g_offset = l_offset
            _error_message = f"expecting '{l_note}'"
            parser_log.add(g_offset, _error_message, forced=forced)

        return res, stream

    return _inner


@word_debug(FMT)
def fn_name(s: str) -> tuple[ElementStream, str]:
    global g_offset

    res, stream = space(s)
    l_offset = g_offset

    RE_FN = re.compile(r"([\w]+)\s*")
    RE_FN2 = re.compile(r"([\w]+)\s*\(")

    result = RE_FN.match(stream)
    if result is None:
        g_offset = l_offset
        return res, stream

    func_name = result.groups()[0]
    if not func_name in FUNCS:

        result2 = RE_FN2.match(stream)
        if result2 is None:
            g_offset = l_offset
            return res, stream
        else:
            result = result2
            func_name = result.groups()[0]

    word = Word(func_name, func_name, WordType.FUNCNAME, l_offset)
    g_offset += len(func_name)

    return [word], stream[len(func_name) :]


@word_debug(FMT)
def left_paren(s: str) -> tuple[ElementStream, str]:
    words, stream = _notation("(")(s)
    if words and len(words) >= 1:
        words[0].word_type = WordType.LEFTPAREN
    return words, stream


@word_debug(FMT)
def right_paren(s: str) -> tuple[ElementStream, str]:
    words, stream = _notation(")", forced=True)(s)
    if words and len(words) >= 1:
        words[0].word_type = WordType.RIGHTPAREN
    return words, stream


@word_debug(FMT)
def comma(s: str) -> tuple[ElementStream, str]:
    words, stream = _notation(",")(s)
    if words and len(words) >= 1:
        words[0].word_type = WordType.COMMA
    return words, stream


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

    def _guess(s):
        return s.lstrip().startswith("(")

    if _GUESS and not _guess(s):
        return [], s

    return _all(left_paren, expr, right_paren)(s)


@word_debug(FMT, is_expr=True)
def e_fn(s: str) -> tuple[ElementStream, str]:
    """expression = fn( expression1 [ , expression2 ]* [,]  )"""

    def _guess(s):
        return s.lstrip()[0].isalpha()

    if _GUESS and not _guess(s):
        return [], s

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
    return _do(_any(e_2, e_1, e_fn), _repeat(_all(operator, expr)))(s)


def parse(s: str, log: ParserLog | None = None) -> ElementStream:
    global g_offset, parser_log

    g_offset = 0
    parser_log = log if log is not None else ParserLog()

    result, stream = expr(s)
    result = [
        item for item in result if item and item.word_type != WordType.PLACEHOLDER
    ]

    _, stream = space(stream)
    if not result:
        if debug_is_on():
            print("unvalid expression!")

        raise ValueError("unvalid expression")

    if stream and len(stream) > 0:
        if debug_is_on():
            print("unvalid expression!")

        raise ValueError(f'can\'t understand "{ stream }"')

    if debug_is_on():
        print("success!")

    return result


def format(s: str) -> str:
    str_list = parse(s)
    # print(str_list)
    if not str_list:
        return ""

    res = " ".join([w.word_str for w in str_list])
    print(res)
    return res


def format2(s: str):
    print("=" * 40)
    print(s)

    buffer = list("-" * (len(s) + 5))

    try:
        word_list = parse(s)
    except ValueError as e:
        # print(e)
        pos, log = parser_log.get()
        buffer[pos] = "^"
        print("".join(buffer))
        print(log)
        return

    for word in word_list:
        match word.word_type:
            case WordType.NUM:
                buffer[word.offset] = "N"
            case WordType.FUNCNAME:
                buffer[word.offset] = "F"
            case WordType.OPERATOR:
                buffer[word.offset] = "O"
            case WordType.COMMA:
                buffer[word.offset] = ","
            case WordType.LEFTPAREN | WordType.RIGHTPAREN:
                buffer[word.offset] = "P"
            case WordType.REGISTER:
                buffer[word.offset] = "@"
            case _:
                buffer[word.offset] = "^"

    print("".join(buffer))


if __name__ == "__main__":
    # open_debug()
    # parse("(2 + 4 * 4 --4 * 12) + 1 + ((-2 + 12)) ")
    format2(" 2, ( 2 * sum (1, max(2, 3), 4, 5 )) - 1")
    format2("( 2 * sum 1, max(2, 3), 4, 5 )) - 1")
    format2(" 2 + ( @aa * sum(1, max(2, 3), 4, 5 )) - (abs(-10) + 1 + 1")
    format2("  sum (1, , 2 ) ")

    # parse("max(1)")
    # parse("max(1,)")
    # parse("max(1, 2,)")
    # parse(
    #     " 2 + ( 2 * sum (1, max(2, (3), ), sum(1,1+1+1), min((5), 6, 7, 8 ))) - 1"
    # )
    # parse("  234  ")
