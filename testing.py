import unittest
from words import number, parse
from calculator import calculate


def _number(s: str):
    res, _ = number(s)
    return res


def _calculate(s: str):
    decimal = calculate(s)
    return str(decimal)


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

        self.assertFalse(_number(" - 123"), msg="should Not be Number")
        self.assertFalse(_number(" - 123"), msg="should Not be Number")
        self.assertFalse(_number(" -a123"), msg="should Not be Number")
        self.assertFalse(_number(" a-123"), msg="should Not be Number")
        self.assertFalse(_number(" .123"), msg="should Not be Number")

    def test_expression(self):
        self.assertTrue(parse("  123  "), msg="should be Expression")
        self.assertTrue(parse("  -123  "), msg="should be Expression")
        self.assertTrue(parse("  123.12  "), msg="should be Expression")
        self.assertTrue(parse("  -123.12  "), msg="should be Expression")
        self.assertTrue(parse("  (123.12)  "), msg="should be Expression")
        self.assertTrue(parse("  (-123.12)  "), msg="should be Expression")
        self.assertTrue(parse("  ( -123.12 )  "), msg="should be Expression")
        self.assertTrue(parse(" 123.12 - 12.3"), msg="should be Expression")
        self.assertTrue(parse(" 123.12 - -12.3"), msg="should be Expression")
        self.assertTrue(parse(" 123.12 - +12.3"), msg="should be Expression")
        self.assertTrue(parse(" 123.12 - (-12.3)"), msg="should be Expression")
        self.assertTrue(parse(" 123.12 - (+12.3)"), msg="should be Expression")
        self.assertTrue(
            parse(" ( 123.12 - (-12.3) )"), msg="should be Expression"
        )
        self.assertTrue(
            parse(" ( 123.12 - (+12.3)) + 1"), msg="should be Expression"
        )
        self.assertTrue(
            parse(" ( (( 4.12 /(123.12 * 15))+ 1 ) - (+12.3)) + 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" 2 * ( 123.12 - (+12.3)) + 1"), msg="should be Expression"
        )
        self.assertTrue(
            parse(" ( (123.12 - +12.3) - 1) / 3"), msg="should be Expression"
        )
        self.assertTrue(
            parse(
                " ( (123.12 - -12.3) - 1) / ( 3 + ( ( 1 * 2 ) / ( 3 + ( 5*(6-1) - 12.1) - 1)))"
            ),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" max(1) "),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" sum(1, 2) "),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" max (1, 2, 3, 4, 5) "),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" max (1, 2, 3, 4, 5 ,) "),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" 1 + sum (1, 2, 3, 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" 1 + sum (1, 2 - 3, 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" 1 + sum (1, (2 - 3), 4, 5 ,) - 1"),
            msg="should be Expression",
        )
        self.assertTrue(
            parse(" 1 + ( sum (1, max(2, 3), 4, 5 ,)) - 1"),
            msg="should be Expression",
        )

        self.assertFalse(parse(" a "), msg="should NOT be Expression")
        self.assertFalse(parse(" - 123 "), msg="should NOT be Expression")
        self.assertFalse(
            parse(" - 123 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            parse(" 12  3 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            parse(" ( 12  3 * * 123 "), msg="should NOT be Expression"
        )
        self.assertFalse(
            parse(" (() 12 *  123 )"), msg="should NOT be Expression"
        )
        self.assertFalse(
            parse(" (( 12 + 3 * 123 )"), msg="should NOT be Expression"
        )
        self.assertFalse(
            parse(" ( 12 - 3 *  123 ) + (5 * 6))"),
            msg="should NOT be Expression",
        )
        self.assertFalse(parse(" ss(1,2)"), msg="should NOT be Expression")
        self.assertFalse(parse(" sum()"), msg="should NOT be Expression")

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


if __name__ == "__main__":
    unittest.main()
