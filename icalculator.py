import sys
import re
from decimal import Decimal
from calculator import calculate
from queueregister import QueueRegister

from colorama import Fore, Back, Style

DEBUG = False

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
        "Input content to calculate.\n"
        + Fore.RED
        + "'exit'"
        + Style.RESET_ALL
        + " to exit.\n"
        + Fore.RED
        + "'$_'  "
        + Style.RESET_ALL
        + " return previous step result."
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
        print(Fore.GREEN + ">>> ", end="")
        sys.stdout.flush()
        x = str(input())

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
