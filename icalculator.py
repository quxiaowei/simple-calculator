import sys
import re
from enum import Enum
from decimal import Decimal

from colorama import Fore, Back, Style

if not __package__:
    from calculator import calculate
    from queueregister import QueueRegister
else:
    from .calculator import calculate
    from .queueregister import QueueRegister


class Mode(Enum):
    WALKING = 1
    STAY = 2


DEBUG = False

VERSION = "0.0.1"

MODE: Mode = Mode.WALKING

register = QueueRegister[Decimal]()


def replace_symbols(input: str) -> str:
    new_str = input
    m = re.findall(r"\$[a-z,_]{1}", new_str)
    for item in set(m):
        symbol = item[1]

        if (
            not register.contains(symbol)
            and symbol != register.PREVIOUS_SYMBOL
        ):
            raise ValueError(f"register { item } does not exists")

        value = str(register[symbol])
        new_str = new_str.replace(item, value)

    DEBUG and print(f"match:{ m }, replace:{ new_str }")
    return new_str


def _header() -> str:
    return (
        f"{ Fore.BLUE }QCalc { VERSION }  [ a calculator in interactive mode ]. { Style.RESET_ALL }\n"
        + f"> Input content to calculate.\n"
        + f'> Type "exit" to exit.\n'
        + f'> Type "ref" for reference.\n'
        + f"> Every result is stored in register from { Fore.BLUE }[a-z]{ Style.RESET_ALL } cyclically.\n"
        + f'> "$a" gives the value in "a".\n'
        + f'> "$_" gives the previous result.'
    )


def _error(error) -> str:
    return (
        Style.RESET_ALL
        + f"{ Back.RED }error:{ Style.RESET_ALL }{ Fore.RED } { error }"
        + Style.RESET_ALL
    )


def _result(cursor, result) -> str:
    return (
        Fore.RED
        + Style.BRIGHT
        + f"${ cursor }: "
        + Style.RESET_ALL
        + Fore.YELLOW
        + f"{ result }"
        + Style.RESET_ALL
    )


def _message(message) -> str:
    return Fore.YELLOW + f"{ message }" + Style.RESET_ALL


def _prompt() -> str:
    if MODE == Mode.WALKING:
        return Fore.BLUE + ">>> "
    else:
        return Fore.BLUE + "=== "


def icalculate():
    global MODE
    print(_header())
    sys.stdout.flush()

    while True:
        print(_prompt(), end="")
        sys.stdout.flush()

        x = str(input()).strip()
        match x:
            case "exit":
                return
            case "back":
                register.go_back()
                continue
            case "show":
                show_results()
                continue
            case "reset" | "clear":
                reset_queue()
                continue
            case "stop" | "stay":
                MODE = Mode.STAY
                register.go_back()
                continue
            case "go":
                MODE = Mode.WALKING
                register.next_one()
                continue
            case "ref":
                show_ref()
                continue

        try:
            x = replace_symbols(x)
            result = calculate(x)
        except ValueError as e:
            print(_error(e), file=sys.stderr)
            sys.stderr.flush()
            continue

        register.write(result)

        print(_result(register.get_cursor(), result))
        sys.stdout.flush()

        if MODE == MODE.WALKING:
            register.next_one()


def show_ref():
    _docstring = """
--- Commands ---
"exit" exit program.
"show" show all results in register.
"clear" or "reset" clear all results in register.
"stay" or "stop" stop the moving of register.
"go" recover the moving of register.

--- Functions ---
sum(1,2,2+1)     => 6
max(1,sum(2,1))  => 3
min(1,2)         => 1
abs(1-12)        => 11 
"""
    print(_message(_docstring))
    pass


def reset_queue():
    global register
    register = QueueRegister[Decimal]()
    print(_message('the results are cleared, starting from "a"'))
    pass


def show_results():
    count = 0
    for key in reversed(register.keys()):
        if register[key] is not None:
            count += 1
            print(_result(key, register[key]))

    if MODE == Mode.STAY:
        if register[0] is not None:
            count += 1
            print(_result(register.get_cursor(), register[0]))

    if count <= 0:
        print(_message("emtry!"))
        sys.stdout.flush()

    sys.stdout.flush()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
