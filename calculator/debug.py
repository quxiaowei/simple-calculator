import functools

_DEBUG_FLAG = False

_INDENT_CHARACTOR = "|   "

_debug_offset = ""


def open_debug():
    global _DEBUG_FLAG
    _DEBUG_FLAG = True


def debug_is_on():
    return _DEBUG_FLAG


def word_debug(fmt, is_expr=False):
    def _inner(func):

        #### for less recursive layers,
        #### remove debug wrapper, when debug mode is off.
        if _DEBUG_FLAG == False:
            return func

        @functools.wraps(func)
        def _inner2(*args, **kwargs):
            global _debug_offset

            _debug_offset += _INDENT_CHARACTOR
            offset = _debug_offset[len(_INDENT_CHARACTOR) :]

            if is_expr and _DEBUG_FLAG:
                print(f"{offset}func <{func.__name__}> \t<= {args[0]}")

            result = func(*args, **kwargs)

            if _DEBUG_FLAG:
                indicator = "🟢"
                result_list = [item.word_str for item in result[0] if item]
                resultStr = " ".join(result_list)
                if not result[0]:
                    indicator = "🔴"
                    resultStr = result[0]

                print(
                    f"{offset}",
                    fmt.format(args, resultStr, func.__name__, indicator),
                )

            _debug_offset = _debug_offset[: -len(_INDENT_CHARACTOR)]

            return result

        return _inner2

    return _inner
