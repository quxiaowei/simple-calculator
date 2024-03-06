import sys
import os
import re
from enum import Enum
from decimal import Decimal


try:
    ### import readline fix input() for macos
    import readline
except ImportError:
    ### readline is not available in windows
    pass

from colorama import Fore, Back, Style

if not __package__:
    from calculator import calculate_num, ParserLogger, Number, RItem
    from queueregister import QueueRegister
else:
    from .calculator import calculate_num, ParserLogger, Number, RItem
    from .queueregister import QueueRegister

__all__ = ["icalculate", "_red", "_blue", "_green"]


class Mode(Enum):
    """register mode: WALKING/STAY"""

    WALKING = 1
    """ walking """

    STAY = 2
    """ stay """


DEBUG = False
"""Debug switch"""

VERSION = "0.0.1"
"""Version"""

MODE: Mode = Mode.WALKING
"""register mode"""

register = QueueRegister[RItem]()
""" Register """

parser_logger: ParserLogger
""" Parser logger"""


def _header() -> str:
    """terminal: header output"""

    return (
        f"{ Fore.BLUE }QCalc { VERSION }  "
        + f"[ a calculator in interactive mode ]. { Style.RESET_ALL }\n"
        + f"> Input content to calculate.\n"
        + f'> Type "exit" to exit.\n'
        + f'> Type "ref" for reference.\n'
        + f"> Every result is stored in register from { Fore.BLUE }[a-z]{ Style.RESET_ALL } cyclically.\n"
        + f'> "@a" gives the value in "a".\n'
        + f'> "@@" gives the previous result.'
    )


def _error(error, message: str | None = None) -> str:
    """terminal: error output"""

    res = ""
    match error:
        case str():
            res = (
                Style.RESET_ALL
                + f"{ Fore.RED }Error:{ Style.RESET_ALL }{ Fore.RED } { error }"
                + Style.RESET_ALL
            )
        case _:
            res = (
                Style.RESET_ALL
                + f"{ Fore.RED }Error:{ Style.RESET_ALL }{ Fore.RED } { error.args[0] }"
                + Style.RESET_ALL
            )

    if message is not None:
        res = Fore.RED + message + Style.RESET_ALL

    return res


def _printable_len(s: str) -> str:
    ss = re.sub(r".\[\d+m", "", s)
    count = 0
    for c in list(ss):
        if c.isprintable():
            count += 1
    return count


def _result(cursor: str, item: RItem) -> str:
    """terminal: result output"""

    size = os.get_terminal_size()
    w_cols = min(size.columns, 60)

    SEP = 5

    s_result = (
        Fore.RED
        + Style.BRIGHT
        + f"@{cursor}: "
        + Style.RESET_ALL
        + Fore.YELLOW
        + f"{item.value}"
        + Style.RESET_ALL
    )
    len_res = _printable_len(s_result)

    s_tag = Fore.WHITE + f'"{item.tag}"' + Style.RESET_ALL
    len_tag = _printable_len(s_tag)

    zlen = w_cols - len_res - len_tag

    if zlen < SEP:
        if w_cols < s_tag:
            s_tag = s_tag[:w_cols-1]+"…"
        return s_result + "\n" + s_tag[:w_cols]

    return s_result + " "*zlen + s_tag

    # return (
    #     Fore.RED
    #     + Style.BRIGHT
    #     + f"@{ cursor }: "
    #     + Style.RESET_ALL
    #     + Fore.YELLOW
    #     + f"{ item.value:<20}"
    #     + Fore.WHITE
    #     + '\t "'
    #     + item.tag
    #     + '"'
    #     + Style.RESET_ALL
    # )


def _result2(cursor: str, item: RItem) -> str:
    """terminal: result output"""

    return (
        Fore.CYAN
        + f"@{cursor}: "
        + f"{item.value}"
        + Style.RESET_ALL
    )


def _message(message) -> str:
    """terminal: message output"""

    return Fore.YELLOW + f"{ message }" + Style.RESET_ALL


def _blue(message) -> str:
    """terminal: blue output"""

    return Fore.BLUE + f"{ message }" + Style.RESET_ALL


def _red(message) -> str:
    """terminal: blue output"""

    return Fore.RED + f"{ message }" + Style.RESET_ALL


def _yellow(message) -> str:
    """terminal: blue output"""

    return Fore.YELLOW + f"{ message }" + Style.RESET_ALL


def _green(message) -> str:
    """terminal: blue output"""

    return Fore.GREEN + f"{ message }" + Style.RESET_ALL


def _prompt() -> str:
    """terminal: prompt output"""

    if MODE == Mode.WALKING:
        return Fore.BLUE + ">>> "
    else:
        return Fore.BLUE + "=== "


def icalculate(stay=True):
    """iteractive processor"""

    global MODE, parser_logger

    print(_header())
    sys.stdout.flush()

    MODE = Mode.STAY if stay else Mode.WALKING

    while True:
        x = str(input(_prompt())).strip().lower()
        cmds = x.split(" ", maxsplit=1)
        cmd: str = cmds[0]
        tag: str = cmds[1] if len(cmds) > 1 else ""
        result: Number

        match cmd:
            case "exit":
                return
            case "back":
                register.go_back()
                continue
            case "show":
                show_results()
                continue
            case "save":
                if MODE == Mode.STAY:
                    try:
                        ritem = register.read(register.cursor)
                        if tag and len(tag) > 0:
                            ritem.tag = tag
                        print(_result(register.cursor, ritem))
                        register.next_one()
                    except ValueError as e:
                        print(_error("no value to save!"))
                else:
                    print(_message("'save' does not work in walking mode"))

                continue
            case "tag":
                pass
            case "reset" | "clear":
                reset_queue()
                continue
            case "stop" | "stay":
                if MODE == Mode.WALKING:
                    MODE = Mode.STAY
                    register.go_back()
                continue
            case "go":
                if MODE == Mode.STAY:
                    MODE = Mode.WALKING
                    register.next_one()
                continue
            case "ref":
                show_ref()
                continue

        try:
            # x = replace_symbols(x)
            parser_logger = ParserLogger()
            l_result = calculate_num(
                input=x,
                register=register,  ###lambda x: register[x.removeprefix("@")],
                logger=parser_logger,
            )

            if l_result is None:
                raise ValueError("not valid")

            result = l_result

        except ValueError as e:
            print(_error(e, parser_logger.message(x)), file=sys.stderr)
            sys.stderr.flush()
            continue

        tag = x
        ritem = RItem(result.value, tag=tag)
        register.write(ritem)

        if MODE == Mode.STAY:
            print(_result2(register.cursor, ritem))
        else:
            print(_result(register.cursor, ritem))

        sys.stdout.flush()

        if MODE == MODE.WALKING:
            register.next_one()


def show_ref():
    """print calculator reference"""

    _docstring = """
--- Commands ---
"exit" exit program.
"show" show all results in register.
"clear" or "reset" clear all results in register.
"stay" or "stop" stop the moving of register.
"go" recover the moving of register.

--- Functions ---
sum(1, 2, 2+1)     => 6
max(1, sum(2, 1))  => 3
min(1, 2)          => 1
abs(1-12)          => 11 
"""
    print(_message(_docstring))
    pass


def reset_queue():
    """reset register to initial status"""

    global register
    register = QueueRegister[RItem]()
    print(_message('the results are cleared, starting from "a"'))


def show_results():
    """print register values"""

    count = 0

    for key, item in reversed(register.items()):
        if key == register.cursor:
            if MODE == Mode.STAY:
                print(_result2(key, item))
                count += 1
            continue

        print(_result(key, item))
        count += 1

    if count <= 0:
        print(_message("emtry!"))

    sys.stdout.flush()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
