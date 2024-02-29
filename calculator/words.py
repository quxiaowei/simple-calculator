import re
from typing import Callable

if not __package__:
    from define import FUNC_SET, OPERATOR_SET, Word, WordType, WordList
    from parserlogger import ParserLogger
    from debug import word_debug, debug_is_on, open_debug
else:
    from .define import FUNC_SET, OPERATOR_SET, Word, WordType, WordList
    from .parserlogger import ParserLogger
    from .debug import word_debug, debug_is_on, open_debug

__all__ = ["parse", "number", "ParserLogger", "format", "Word", "WordList"]


ExprFunc = Callable[[str], tuple[WordList, str]]
"""Type alias: Expression Function"""


### constants
FMT = "{3} {1!r} \t: {2}"
# RE_NO = re.compile(r"[-+]?[0-9]+(,[0-9]{3})*(\.[0-9]+)?([Ee][-+]?[0-9]+)?")
RE_NO = re.compile(r"[-+]?[0-9]+(\.[0-9]+)?([Ee][-+]?[0-9]+)?\b")
RE_HEX_NO = re.compile(r"0[Xx][0-9a-fA-F]+\b")
RE_OCT_NO = re.compile(r"0[Oo][0-7]+\b")
RE_REGISTER = re.compile(r"(@@)|(@[a-z0-9]+)\b")
RE_FN = re.compile(r"([\w]+)\s*")
RE_FN2 = re.compile(r"([\w]+)\s*\(")


### init
if __name__ == "__main__":
    # open_debug()
    pass


parser_logger: ParserLogger
"""logger"""

parser_offset: int
"""offset of input string during parsing"""

word_list: WordList
"""word list"""


def _expect(type: WordType, at: int, forced: bool = False):
    """Expecting word type

    Args:
        at:     position in raw input
        type:   word type
        forced: higher priority (default False)
    Returns:
        None
    """
    global parser_logger, word_list

    def _left_type(type: WordType) -> str:
        l_type = (
            "operand"
            if type in {WordType.NUM, WordType.REGISTER, WordType.RIGHTPAREN}
            else "operator"
        )
        return l_type

    def _right_type(type: WordType) -> str:
        l_type: str = (
            "operand"
            if type in {WordType.NUM, WordType.REGISTER}
            else "operator"
        )
        return l_type

    l_text = f"expecting {type.value}"
    l_type = type

    if at not in parser_logger or not parser_logger[at]:
        parser_logger[at] = (l_text, l_type, 0)
        return

    if len(word_list) > 1:
        prev_word = word_list[-1]
        prev_type = _left_type(prev_word.type)
    else:
        prev_type = _left_type(WordType.PLACEHOLDER)

    curr_type = _right_type(l_type)
    old_type = _right_type(parser_logger[at][1])

    if old_type == curr_type:
        if forced:
            parser_logger[at] = (l_text, l_type, 0)
        return

    if prev_type != curr_type:
        parser_logger[at] = (l_text, l_type, 0)
        return


def _all(*fns: ExprFunc) -> ExprFunc:
    """expression = expression1 expression2 ... expressionN

    Args:
        fns: Expression Functions
    Returns:
        new expression func
    """

    def _inner(s: str) -> tuple[WordList, str]:
        global parser_offset, word_list
        l_offset = parser_offset
        l_word_count = len(word_list)

        res, stream = [], s
        for fn in fns:
            res_tmp, stream = fn(stream)
            if not res_tmp:
                parser_offset = l_offset
                word_list = word_list[:l_word_count]
                return [], s
            res += res_tmp

        return res, stream

    return _inner


def _any(*fns: ExprFunc) -> ExprFunc:
    """expression = expression1 | expression2 | ... | expressionN

    Args:
        fns: expression functions
    Returns:
        new expression func
    """

    def _inner(s: str) -> tuple[WordList, str]:
        global parser_offset, word_list
        l_offset = parser_offset
        l_word_count = len(word_list)

        res, stream = [], s
        for fn in fns:
            res, stream = fn(stream)
            if res:
                return res, stream

            parser_offset = l_offset
            word_list = word_list[:l_word_count]
            res, stream = [], s

        return res, stream

    return _inner


def _do(*fns: ExprFunc) -> ExprFunc:
    """expression = expression1 [ expression2 ... [ expressionN ]...]

    Args:
        fns: expression functions
    Returns:
        new expression func
    """

    def _inner(s: str) -> tuple[WordList, str]:
        global parser_offset, word_list
        l_offset = parser_offset
        l_word_count = len(word_list)

        res, stream = [], s
        for fn in fns:
            _stream = stream
            res_tmp, stream = fn(stream)
            if not res_tmp:
                stream = _stream
                parser_offset = l_offset
                word_list = word_list[:l_word_count]
                break

            l_offset = parser_offset
            l_word_count = len(word_list)
            res += res_tmp

        return res, stream

    return _inner


def _repeat(fn: ExprFunc, *, at_least_once=False) -> ExprFunc:
    """expression = expression*

    Args:
        fn: expression function
        at_least_once: if True ( expression = expression+ )
    Returns:
        new expression func
    """

    def _inner(s: str) -> tuple[WordList, str]:
        global parser_offset, word_list
        l_offset = parser_offset
        l_word_count = len(word_list)

        res, stream = [], s

        _stream = stream

        res_tmp, stream = fn(stream)
        while res_tmp:
            l_offset = parser_offset
            l_word_count = len(word_list)
            _stream = stream

            res += res_tmp
            res_tmp, stream = fn(stream)

        stream = _stream

        parser_offset = l_offset
        word_list = word_list[:l_word_count]

        if not res:
            res, stream = [], s

        if not res and not at_least_once:
            res, stream = [Word.placeholder()], s

        return res, stream

    return _inner


def space(s: str) -> tuple[WordList, str]:
    global parser_offset
    l_offset = parser_offset

    for i, c in enumerate(s):
        if not c.isspace():
            return [], s[i:]
        parser_offset += 1
    return [], ""


@word_debug(FMT)
def number(s: str) -> tuple[WordList, str]:
    global _error_message, parser_offset, word_list

    res, stream = space(s)
    l_offset = parser_offset

    l_type = WordType.NUM

    match list(stream[:2].lower()):
        case ["0", "x"]:
            result = RE_HEX_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 16))
                word = Word(result.group(), num_str, l_type, l_offset)

        case ["0", "o"]:
            result = RE_OCT_NO.match(stream)
            if result is not None:
                num_str = str(int(result.group(), 8))
                word = Word(result.group(), num_str, l_type, l_offset)

        case ["@", _]:
            result = RE_REGISTER.match(stream)
            l_type = WordType.REGISTER
            if result is not None:
                num_str = result.group()
                word = Word(result.group(), num_str, l_type, l_offset)

        case _:
            result = RE_NO.match(stream)
            if result is not None:
                num_str = result.group()
                word = Word(result.group(), num_str, l_type, l_offset)

    if result is None:
        parser_offset = l_offset
        _expect(l_type, at=parser_offset)
        return res, stream

    # num_str = result.group()
    word_list.append(word)

    span = result.span()
    parser_offset += span[1]
    return [word], stream[span[1] :]


@word_debug(FMT)
def operator(s: str) -> tuple[WordList, str]:
    global parser_offset, word_list

    res, stream = space(s)
    l_offset = parser_offset

    for token in OPERATOR_SET:
        if stream.startswith(token):
            stream = stream[len(token) :]
            word = Word(token, token, WordType.OPERATOR, l_offset)
            word_list.append(word)
            res.append(word)

            parser_offset += len(token)
            break
    else:
        parser_offset = l_offset
        _expect(WordType.OPERATOR, at=parser_offset)

    return res, stream


def _notation(
    note: str,
    type: WordType,
    *,
    drop=False,
    forced=False,
) -> ExprFunc:

    def _inner(s: str) -> tuple[WordList, str]:
        global parser_offset, word_list

        res, stream = space(s)
        l_offset = parser_offset

        l_note = note.strip()

        if stream.startswith(l_note):
            parser_offset += len(l_note)
            if drop:
                res.append(Word.placeholder())
                pass
            else:
                word = Word(note, note, type, l_offset)
                word_list.append(word)
                res.append(word)

            stream = stream[len(l_note) :]
        else:
            parser_offset = l_offset
            _expect(type, at=parser_offset, forced=forced)

        return res, stream

    return _inner


@word_debug(FMT)
def fn_name(s: str) -> tuple[WordList, str]:
    global parser_offset

    res, stream = space(s)
    l_offset = parser_offset

    result = RE_FN.match(stream)
    if result is None:
        parser_offset = l_offset
        return res, stream

    func_name = result.groups()[0]
    if not func_name in FUNC_SET:

        result2 = RE_FN2.match(stream)
        if result2 is None:
            parser_offset = l_offset
            return res, stream
        # else:
        result = result2
        func_name = result.groups()[0]

    word = Word(func_name, func_name, WordType.FUNCNAME, l_offset)
    word_list.append(word)
    parser_offset += len(func_name)

    return [word], stream[len(func_name) :]


@word_debug(FMT)
def left_paren(s: str) -> tuple[WordList, str]:
    words, stream = _notation("(", WordType.LEFTPAREN)(s)
    return words, stream


@word_debug(FMT)
def right_paren(s: str) -> tuple[WordList, str]:
    words, stream = _notation(")", WordType.RIGHTPAREN, forced=True)(s)
    return words, stream


@word_debug(FMT)
def comma(s: str) -> tuple[WordList, str]:
    words, stream = _notation(",", WordType.COMMA)(s)
    return words, stream


@word_debug(FMT)
def trailing_comma(s: str) -> tuple[WordList, str]:
    words, stream = _notation(",", WordType.TRAILINGCOMMA)(s)
    return words, stream


@word_debug(FMT, is_expr=True)
def e_2(s: str) -> tuple[WordList, str]:
    """expression = number [ operator number ]*"""

    return _do(number, _repeat(_all(operator, number)))(s)


@word_debug(FMT, is_expr=True)
def e_1(s: str) -> tuple[WordList, str]:
    """expression = '(' expression ')'"""

    return _all(left_paren, expr, right_paren)(s)


@word_debug(FMT, is_expr=True)
def e_fn(s: str) -> tuple[WordList, str]:
    """expression = fn( expression1 [ , expression2 ]* [,]  )"""

    return _all(
        fn_name,
        left_paren,
        _do(expr, _repeat(_all(comma, expr)), trailing_comma),
        right_paren,
    )(s)


@word_debug(FMT, is_expr=True)
def expr(s: str) -> tuple[WordList, str]:
    """expression =  _e2 | _e1 [ operator expression ]*"""
    # _e2 is not necessary, can be replaced by number
    return _do(_any(e_2, e_1, e_fn), _repeat(_all(operator, expr)))(s)


def parse(s: str, *, log: ParserLogger | None = None) -> WordList:
    global parser_offset, parser_logger, word_list

    parser_offset = 0
    parser_logger = log if log is not None else ParserLogger()

    word_list = []

    words, stream = expr(s)
    words = [word for word in words if word and not word.isvirtual]

    _, stream = space(stream)
    if not words:
        raise ValueError("unvalid expression")

    if stream and len(stream) > 0:
        raise ValueError(f'can\'t understand "{ stream }"')

    if debug_is_on():
        print("success!")

    return words


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
        pos, log, _ = parser_logger.get()
        buffer[pos] = "^"
        print("".join(buffer))
        print(log)
        return

    for word in word_list:
        match word.type:
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
