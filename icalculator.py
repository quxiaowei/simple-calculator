import sys
import re
from decimal import Decimal
from calculator import calculate
from queueregister import QueueRegister

DEBUG = False

register = QueueRegister[Decimal]()


def replace_symbols(input: str) -> str:
    new_str = input
    m = re.findall(r"\$[a-z]{1}", new_str)
    for item in set(m):
        symbol = item[1]

        if not register.contains(symbol):
            raise ValueError(f"register { item } does not exists")

        value = str(register[symbol])
        new_str = new_str.replace(item, value)

    DEBUG and print(f"match:{ m }, replace:{ new_str }")
    return new_str


def icalculate():
    print("Input content to calculate, 'exit' to exit")
    sys.stdout.flush()

    while True:
        x = str(input(">>> "))

        if x == "exit":
            return

        try:
            x = replace_symbols(x)
            result = calculate(x)
        except ValueError as e:
            print(f"input error: { e }")
            continue

        register.write(result)

        print(f"${ register.get_cursor() }: {result}")
        sys.stdout.flush()

        register.goto_next()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
