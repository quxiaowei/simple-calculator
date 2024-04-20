# DailyCalc - A Simple Calculator

![PyPI - Version](https://img.shields.io/pypi/v/dailycalc)

**python\>=3.11**

**dependency** : **[colorama](https://pypi.org/project/colorama/)**
(**not mandatory**, if you don't need highlight, you can uninstall it later)

## Description

A simple calculator based on decimal.Decimal.

> Decimal “is based on a floating-point model which was designed with people in mind, and necessarily has a paramount guiding principle – computers must provide an arithmetic that works in the same way as the arithmetic that people learn at school.” – excerpt from the decimal arithmetic specification

Output is rounded with maximum 10 decimal place for Infinitesimal decimals.

```bash
sqrt(2)     => 1.4142135624   # keep 10 decimal places
0.1 + 0.2   => 0.3
ln(exp(10)) => 10.0000000000  # inevitable loss of precision
```

## Usage

install by pip

```bash
pip install dailycalc
```
or
```bash
pipx install dailycalc # only cli tool available
```

import into your code

```python
from dailycalc import calculate, check_calc

if check_calc("sum(123, 3)"):
    print(calculate("sum(123, 3)"))

# or

try:
    print(calculate("sum(123, 3)"))
except ValueError as e:
    print(e)
```

once-off calculate

```bash
python -m dailycalc "sum(0.1, 0.2)"
```

iteractive mode

```bash
python -m dailycalc -i
# or
idailycalc
```

## Operators & Functions

supporting:

`+ - \* / ^`

`sum max min abs round hex oct sqrt log ln exp`

## Interactive mode

Every result is stored in register from \[a-z\] cyclically, that is when reaching the last one "z", the register would go back to "a" and cover the old value.

"@a" gives the value in "a". "@@" gives the previous result.'

for example:

![image](/ext/exp.png)

## Support HEX, OCT, Scientific input

1. `HEX`: `0x12E`, `0X12E` support only integar
2. `OCT`: `0o123`, `0O123` support only integar
3. Scientific Notation: `-123.12E-123` or `-123.12e+123`

## Error message with highlight

![image](./ext/error_message.png)

### Reference for interactive mode

```
--- Modes ---
STAY mode (prompt "===") (Default) save result by call "save" command
WALKING mode (prompt ">>>") automatically save results and move to next register

--- Commands ---
"exit" exit program.
"show" show all results in register.
"reset" clear all results in register.
"stay" switch to STAY mode.
"go" save result & switch to WALKING mode.
"save [tag]" save result (in STAY Mode).

--- Functions ---
sum(1, 2, 2+1)     => 6
max(1, sum(2, 1))  => 3
min(1, 2)          => 1
abs(1-12)          => 11
round(12.16, 1)    => 12.2
hex(10)            => 0xa
oct(10)            => 0o12
sqrt(1.44)         => 1.2
ln(exp(100))       => 10.0000000000
log(100)           => 2
```

## Future Plans

add more function & operator, bugfix.
