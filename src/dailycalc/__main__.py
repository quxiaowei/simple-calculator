#!/usr/bin/env python
import sys
import argparse

if not __package__:
    from calculator import calculate, error_message
    from icalculator import icalculate, VERSION, _red, _green, _blue
else:
    from .calculator import calculate, error_message
    from .icalculator import icalculate, VERSION, _red, _green, _blue


parser = argparse.ArgumentParser(
    prog="dailycalc",
    description="A simple calculator",
)
parser.add_argument(
    "-v", "--version", action="version", version=f"qcalc({VERSION})"
)

parser.add_argument(
    "-i",
    "--interactive",
    required=False,
    action="store_true",
    default=False,
    help="interactive mode. not work with 'input'",
)

parser.add_argument(
    "-s",
    "--stay",
    required=False,
    action="store_true",
    default=True,
    help="STAY mode. not work with non-interactive mode",
)

parser.add_argument(
    "input",
    type=str,
    nargs="?",
    help='string to calculate, wrapped by quots for complex expression. \nexample: "1 + 2 + sum( max( 1, 2))"',
)

args = parser.parse_args()
# print(args)

if args.interactive:
    icalculate(args.stay)
else:
    if args.input and len(args.input) > 0:
        string_input = args.input
    else:
        print(
            _red("input is required in non-interactive mode"),
            file=sys.stderr,
        )
        sys.stderr.flush()
        sys.exit()

    try:
        result = calculate(string_input)
    except:
        print(_red(error_message(string_input)), file=sys.stderr)
        sys.stderr.flush()
    else:
        print(_blue(f"input:  { string_input }"))
        print(_green(f"result: { result }"))
        sys.stdout.flush()
