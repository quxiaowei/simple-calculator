import sys
import re
import readline  ### fix input()
from enum import Enum
from decimal import Decimal

from colorama import Fore, Back, Style

if not __package__:
    from calculator import calculate
    from queueregister import QueueRegister
else:
    from .calculator import calculate
    from .queueregister import QueueRegister

__all__ = ["icalculate"]


class Mode(Enum):
    """
    register mode
    """

    WALKING = 1
    """ walking """
    STAY = 2
    """ stay """


DEBUG = False

VERSION = "0.0.1"

MODE: Mode = Mode.WALKING
""" register mode """

register = QueueRegister[Decimal]()


def replace_symbols(input: str) -> str:
    """
    replace symbol in input with value stored in correspoding register
    """
    new_str = input
    m = re.findall(r"\$[a-z,_]{1}", new_str)
    for item in set(m):
        symbol = item[1]

        if symbol not in register and symbol != register.PREVIOUS_SYMBOL:
            raise ValueError(f"register { item } does not exists")

        value = str(register[symbol])
        new_str = new_str.replace(item, f" {value} ")

    if DEBUG:
        print(f"match:{ m }, replace:{ new_str }")

    return new_str


def _header() -> str:
    """
    terminal: header output
    """
    return (
        f"{ Fore.BLUE }QCalc { VERSION }  "
        + f"[ a calculator in interactive mode ]. { Style.RESET_ALL }\n"
        + f"> Input content to calculate.\n"
        + f'> Type "exit" to exit.\n'
        + f'> Type "ref" for reference.\n'
        + f"> Every result is stored in register from { Fore.BLUE }[a-z]{ Style.RESET_ALL } cyclically.\n"
        + f'> "$a" gives the value in "a".\n'
        + f'> "$_" gives the previous result.'
    )


def _error(error) -> str:
    """
    terminal: error output
    """
    match error:
        case str():
            return (
                Style.RESET_ALL
                + f"{ Back.RED }error:{ Style.RESET_ALL }{ Fore.RED } { error }"
                + Style.RESET_ALL
            )
        case _:
            return (
                Style.RESET_ALL
                + f"{ Back.RED }error:{ Style.RESET_ALL }{ Fore.RED } { error.args[0] }"
                + Style.RESET_ALL
            )


def _result(cursor: str, result: Decimal) -> str:
    """
    terminal: result output
    """
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
    """
    terminal: message output
    """
    return Fore.YELLOW + f"{ message }" + Style.RESET_ALL


def _prompt() -> str:
    """
    terminal: prompt output
    """
    if MODE == Mode.WALKING:
        return Fore.BLUE + ">>> "
    else:
        return Fore.BLUE + "=== "


def icalculate():
    """
    iteractive processor
    """

    global MODE
    print(_header())
    sys.stdout.flush()

    while True:
        x = str(input(_prompt())).strip()
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
            if result is None:
                raise ValueError("not valid")
        except ValueError as e:
            print(_error(e), file=sys.stderr)
            sys.stderr.flush()
            continue

        register.write(result)

        print(_result(register.cursor, result))
        sys.stdout.flush()

        if MODE == MODE.WALKING:
            register.next_one()


def show_ref():
    """
    print calculator reference
    """
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
    """
    reset register to initial status
    """
    global register
    register = QueueRegister[Decimal]()
    print(_message('the results are cleared, starting from "a"'))


def show_results():
    """
    print register values
    """
    count = 0

    for key, value in reversed(register.items()):
        if key == register.cursor and MODE == Mode.WALKING:
            continue
        print(_result(key, value))
        count += 1

    if count <= 0:
        print(_message("emtry!"))

    sys.stdout.flush()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
