# A Simple Calculator

### words.py

validate and parse expression string

### calculate.py

calculate

## 20240211

### add interactive mode in icalculate.py

Results will be recorded in an \[a-z\] register automatically. you can use the `$a` in subsequent calculation. When reaching the last one "z", the register would go back to "a" and cover the old value.

`$_` is constantly pointed previous step value.

for example:

```
>>> 1
$a: 1
>>> $a + 2
$b: 3
...
$z: 351
>>> $z + 1
$a: 352
>>> $_ - 1
$b: 351
```

### support HEX, OCT, Scientific input

1. HEX: "0x12E", "0X12E" only support integar
2. OCT: "0o123", "0O123" only support integar
3. Scientific: "-123.12E-123" or "-123.12e+123"

### add terminal highlight in -i
