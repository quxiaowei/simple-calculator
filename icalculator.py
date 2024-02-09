import sys
import re
from calculator import calculate
from queueregister import QueueRegister

DEBUG = False

register = QueueRegister()


def replace_register(input: str) -> str:
    new_str = input
    m = re.findall(r"\$[a-z]{1}", new_str)
    for item in set(m):
        key = item[1]

        if not register.contains(key):
            raise ValueError(f"register { item } does not exists")

        value = str(register[key])
        new_str = new_str.replace(item, value)

    DEBUG and print(f"match:{ m }, replace:{ new_str }")
    return new_str


def icalculate() -> None:
    print("Input content to calculate, 'exit' to exit")
    sys.stdout.flush()

    while True:
        x = str(input(">>> "))

        if x == "exit":
            return
        try:
            x = replace_register(x)
            result = calculate(x)
        except ValueError as e:
            print(f"input error: { e }")
            continue

        register.write(result)
        print(f"${ register.get_cursor() }: {result}")
        sys.stdout.flush()

        register.next_cursor()


if __name__ == "__main__":
    DEBUG = True
    icalculate()
