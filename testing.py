import unittest
from words import number, parse
from calculator import calculate


def _number(s: str):
    res, _ = number(s)
    return res


def _parse(s: str):
    res = parse(s)
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

        self.assertEqual(_number(" - 123"), [], msg="should Not be Number")
        self.assertEqual(_number(" - 123"), [], msg="should Not be Number")
        self.assertEqual(_number(" -a123"), [], msg="should Not be Number")
        self.assertEqual(_number(" a-123"), [], msg="should Not be Number")
        self.assertEqual(_number(" .123"), [], msg="should Not be Number")

    def test_valid(self):
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
        self.assertTrue(_parse(" 123.12 - (-12.3)"), msg="should be Expression")
        self.assertTrue(_parse(" 123.12 - (+12.3)"), msg="should be Expression")
        self.assertTrue(_parse(" ( 123.12 - (-12.3) )"), msg="should be Expression")
        self.assertTrue(_parse(" ( 123.12 - (+12.3)) + 1"), msg="should be Expression")
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

        self.assertEqual(_parse(" a "), [], msg="should NOT be Expression")
        self.assertEqual(_parse(" - 123 "), [], msg="should NOT be Expression")
        self.assertEqual(_parse(" - 123 * * 123 "), [], msg="should NOT be Expression")
        self.assertEqual(_parse(" 12  3 * * 123 "), [], msg="should NOT be Expression")
        self.assertEqual(
            _parse(" ( 12  3 * * 123 "), [], msg="should NOT be Expression"
        )
        self.assertEqual(_parse(" (() 12 *  123 )"), [], msg="should NOT be Expression")
        self.assertEqual(
            _parse(" (( 12 + 3 * 123 )"), [], msg="should NOT be Expression"
        )
        self.assertEqual(
            _parse(" ( 12 - 3 *  123 ) + (5 * 6))"), [], msg="should NOT be Expression"
        )

    def test_calculate(self):
        self.assertEqual(
            _calculate(
                " 112.01-2.5 +(-2.56 * (31 +1.1) ) * 2.2 + 23.3 * 3.1 + ( 1.1 + 22 * 8 ) "
            ),
            "178.0528",
            msg="should NOT be Expression",
        )


if __name__ == "__main__":
    unittest.main()
