# A Simple Calculator

Based on decimal.Decimal.

> Decimal “is based on a floating-point model which was designed with people in mind, and necessarily has a paramount guiding principle – computers must provide an arithmetic that works in the same way as the arithmetic that people learn at school.” – excerpt from the decimal arithmetic specification

### Require colorama [https://pypi.org/project/colorama/]

### words.py

validate and parse expression string

### calculate.py

calculate

## 20240211

### Add interactive mode in icalculate.py

Every result is stored in register from \[a-z\] cyclically, that is when reaching the last one "z", the register would go back to "a" and cover the old value.

"@a" gives the value in "a". "@@" gives the previous result.'

for example:

```
>>> 1
@a: 1
>>> @a + 2
@b: 3
...
@z: 351
>>> @z + 1
@a: 352
>>> @@- 1
@b: 351
```

### Support HEX, OCT, Scientific input

1. HEX: "0x12E", "0X12E" only support integar
2. OCT: "0o123", "0O123" only support integar
3. Scientific: "-123.12E-123" or "-123.12e+123"

### Add terminal highlight in -i

### Add better error message

```
>>> abs(sum(1,2,3),11)
  Input: abs(sum(1,2,3),11)
         ---------------^^-----
  Error: func abs: expecting 1 parameters got 2
>>>
```

```
>>> sum(1,
  Input: sum(1,
         ------^---
  Error: expecting Number
>>>
```

### reference for interactive mode

```
--- Modes ---
STAY mode (prompt:"===") (Default)
save result by call "save" command
WALKING mode (prompt:">>>")
automatically save results and move to next register
--- Commands ---
"exit" exit program.
"show" show all results in register.
"reset" clear all results in register.
"stay" switch to STAY mode.
"go" save result & switch to WALKING mode.
"save [tag]" save result (in STAY Mode).
--- Functions ---
sum(1, 2, 2+1) => 6
max(1, sum(2, 1)) => 3
min(1, 2) => 1
abs(1-12) => 11
round(12.16, 1) => 12.2
hex(10) => 0xa
oct(10) => 0o12
```

### How to use

linux/mac:

```
python python -m zipapp -p "/usr/bin/env python"  simple_calculator
```

link to pyz file to a new file

```
ln -s simple_calculator.pyz qcalc
```

call it

```
./qcalc -i
```

## Future Plans

bugix & Maybe add a file to store history
