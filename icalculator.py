import sys
import re
from decimal import Decimal
from calculator import calculate
from queueregister import QueueRegister

from colorama import Fore, Back, Style

DEBUG = False

VERSION = "0.0.1"

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


def _header():
    return (
        f"{ Fore.BLUE }QCalc { VERSION }  [ a calculator in interactive mode ]. { Style.RESET_ALL }\n"
        + f'> Input content to calculate. Type { Fore.BLUE }"exit"{ Style.RESET_ALL } to exit.\n'
        + f"> Every result is stored in register from { Fore.BLUE }[a-z]{ Style.RESET_ALL } cyclically.\n"
        + f'> { Fore.BLUE }"$a"{ Style.RESET_ALL } gives the value in "a".\n'
        + f'> { Fore.BLUE }"$_"{ Style.RESET_ALL } gives the previous result.'
    )


def _error(error):
    return (
        Style.RESET_ALL
        + Back.RED
        + f"input error: { error }"
        + Style.RESET_ALL
    )


def _result(cursor, result):
    return (
        Fore.RED
        + Style.BRIGHT
        + f"${ cursor }: "
        + Style.RESET_ALL
        + Fore.YELLOW
        + f"{ result }"
        + Style.RESET_ALL
    )


def icalculate():
    print(_header())
    sys.stdout.flush()

    while True:
        print(Fore.BLUE + ">>> ", end="")
        sys.stdout.flush()
        x = str(input()).strip()

        if x == "exit":
            return

        try:
            x = replace_symbols(x)
            result = calculate(x)
        except ValueError as e:
            print(
                _error(e),
                file=sys.stderr,
            )
            sys.stderr.flush()
            continue

        register.write(result)

        print(_result(register.get_cursor(), result))
        sys.stdout.flush()

        register.goto_next()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
