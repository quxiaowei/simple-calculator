#!/usr/bin/env python

import argparse
import sys
from calculator import calculate
from icalculator import icalculate, VERSION

parser = argparse.ArgumentParser(
    prog="qcalc",
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
    "input",
    type=str,
    nargs="?",
    help='string to calculate, wrapped by quots for complex expression. \nexample: "1 + 2 + sum( max( 1, 2))"',
)

args = parser.parse_args()
# print(args)

if args.interactive:
    icalculate()
else:
    if args.input and len(args.input) > 0:
        string_input = args.input
        print(f"input: { string_input }")
    else:
        print("input is required in non-interactive mode", file=sys.stderr)
        sys.stderr.flush()

    try:
        result = calculate(string_input)
    except:
        print("error: check your input", file=sys.stderr)
        sys.stderr.flush()
    else:
        print(f"result: { result }")
        sys.stdout.flush()
