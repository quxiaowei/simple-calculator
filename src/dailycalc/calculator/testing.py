import unittest
import decimal

if not __package__:
    from words import number, parse
    from calculator import calculate
else:
    from .words import number, parse
    from .calculator import calculate


def _number(s: str):
    res, _ = number(s)
    return res


def _parse(s: str):
    try:
        return parse(s)
    except ValueError:
        return False


def _calculate(s: str):
    try:
        decimal = calculate(s)
        return str(decimal)
    except ValueError:
        return None


class Testing(unittest.TestCase):
    def test_number(self):
        self.assertTrue(_number("  123  "), msg="should be Number")
        self.assertTrue(_number("  123.0  "), msg="should be Number")
        self.assertTrue(_number("  123.12  "), msg="should be Number")
        self.assertTrue(_number("  -123  "), msg="should be Number")
        self.assertTrue(_number("  -123.234  "), msg="should be Number")
        self.assertTrue(_number("  +123  "), msg="should be Number")
        self.assertTrue(_number("  +123.234  "), msg="should be Number")
        self.assertTrue(_number("  -0  "), msg="should be Number")
        self.assertTrue(_number("  -0.234  "), msg="should be Number")
        self.assertTrue(_number("  +0  "), msg="should be Number")
        self.assertTrue(_number("  +0.234  "), msg="should be Number")
        self.assertTrue(_number("  +0.234 a "), msg="should be Number")
        self.assertTrue(_number("  +0.234.0 "), msg="should be Number")
        self.assertTrue(_number("  0.234E21 "), msg="should be Number")
        self.assertTrue(_number("  +0.234e-21 "), msg="should be Number")
        self.assertTrue(_number("  -0.234e+21 "), msg="should be Number")

        self.assertFalse(_number(" - 123"), msg="should Not be Number")
        self.assertFalse(_number(" - 123"), msg="should Not be Number")
        self.assertFalse(_number(" -a123"), msg="should Not be Number")
        self.assertFalse(_number(" a-123"), msg="should Not be Number")
        self.assertFalse(_number(" .123"), msg="should Not be Number")

    def test_expression(self):
        self.assertTrue(_parse("  123  "), msg="should be Expression")
        self.assertTrue(_parse("  -123  "), msg="should be Expression")
        self.assertTrue(_parse("  123.12  "), msg="should be Expression")
        self.assertTrue(_parse("  -123.12  "), msg="should be Expression")
        self.assertTrue(_parse("  (123.12)  "), msg="should be Expression")
        self.assertTrue(_parse("  (-123.12)  "), msg="should be Expression")
        self.assertTrue(_parse("  ( -123.12 )  "), msg="should be Expression")
        self.assertTrue(_parse(" 123.12 - 12.3"), msg="should be Expression")
        self.assertTrue(_parse(" 123.12 - -12.3"), msg="should be Expression")
        self.assertTrue(_parse(" 123.12 - +12.3"), msg="should be Expression")
        self.assertTrue(
            _parse(" 123.12 - (-12.3)"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(" 123.12 - (+12.3)"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(" ( 123.12 - (-12.3) )"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(" ( 123.12 - (+12.3)) + 1"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(" ( (( 4.12 /(123.12 * 15))+ 1 ) - (+12.3)) + 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" 2 * ( 123.12 - (+12.3)) + 1"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(" ( (123.12 - +12.3) - 1) / 3"), msg="should be Expression"
        )
        self.assertTrue(
            _parse(
                " ( (123.12 - -12.3) - 1) / ( 3 + ( ( 1 * 2 ) / ( 3 + ( 5*(6-1) - 12.1) - 1)))"
            ),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" max(1) "),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" sum(1, 2) "),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" max (1, 2, 3, 4, 5) "),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" max (1, 2, 3, 4, 5 ,) "),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" 1 + sum (1, 2, 3, 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" 1 + sum (1, 2 - 3, 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" 1 + sum (1, (2 - 3), 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            _parse(" 1 + ( sum (1, max(2, 3), 4, 5 ,)) - 1"),
            msg="should be Expression",
        )

        self.assertFalse(_parse(" a "), msg="should NOT be Expression")
        self.assertFalse(_parse(" - 123 "), msg="should NOT be Expression")
        self.assertFalse(
            _parse(" - 123 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            _parse(" 12  3 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            _parse(" ( 12  3 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            _parse(" (() 12 *  123 )"), msg="should NOT be Expression"
        )
        self.assertFalse(
            _parse(" (( 12 + 3 * 123 )"), msg="should NOT be Expression"
        )
        self.assertFalse(
            _parse(" ( 12 - 3 *  123 ) + (5 * 6))"),
            msg="should NOT be Expression",
        )
        self.assertTrue(_parse(" ss(1,2)"), msg="should be Expression")
        self.assertFalse(_parse(" sum()"), msg="should NOT be Expression")

    def test_calculate(self):
        self.assertEqual(
            _calculate(
                " 112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) "
            ),
            "178.0528",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  sum (1,) "),
            "1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  max (1) "),
            "1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  min (1) "),
            "1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  sum (1,2,) "),
            "3",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  max (2.3, 2,) "),
            "2.3",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("  min (2.3,2.1) "),
            "2.1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(
                " 2 + ( 2 * sum (1, max(2, (3)), sum(1,1+1+1), min((5), 6, 7, 8 ))) - 1"
            ),
            "27",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" +1E+2 + 1"),
            "101",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" +1E+2 + 1"),
            "101",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" +1E-2 + 1"),
            "1.01",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" 1+5^2+1"),
            "27",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" 2*5^2/5"),
            "10",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate(" 2*25^(1/2)/2"),
            "5",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("abs(-1.1)"),
            "1.1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("round(1.12, 1)"),
            "1.1",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("round(1.15, 1)"),
            "1.2",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("round(1.16, 1)"),
            "1.2",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("log(100)"),
            "2",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("round(exp(ln(50)), 0)"),
            "50",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("round(ln(exp(50)), 0)"),
            "50",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("sqrt(1.44)"),
            "1.2",
            msg="should be Equal",
        )
        self.assertEqual(
            _calculate("sqrt(2)"),
            "1.4142135624",
            msg="should be Equal",
        )
        with self.assertRaises(ValueError):
            calculate(" 2/0")

        with self.assertRaises(ValueError):
            calculate("abs(1,1)")

        with self.assertRaises(ValueError):
            calculate("round(11,1.1)")


if __name__ == "__main__":
    unittest.main()
