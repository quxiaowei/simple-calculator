from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable, Self, Any


__all__ = [
    "FUNCS",
    "OPERATOR_SET",
    "WordType",
    "Word",
    "WordList",
    "Number",
    "Operator",
    "Register",
]


class WordType(Enum):
    """word type"""

    NUM = "Number"
    OPERATOR = "Operator"
    FUNCNAME = "Function"
    NOTATION = "Notation"
    COMMA = "','"
    LEFTPAREN = "'('"
    RIGHTPAREN = "')'"
    REGISTER = "Register"

    # virtual words
    PLACEHOLDER = "P"
    """placeholder"""
    TRAILINGCOMMA = "TC"
    """trailing comma"""

    @property
    def isvirtual(self) -> bool:
        return self == WordType.PLACEHOLDER or self == WordType.TRAILINGCOMMA


@dataclass
class Word:
    """Class: Word"""

    word_str: str
    """raw string"""
    value_str: str
    """value string"""
    type: WordType
    """type"""
    offset: int = 0
    """postion in raw input"""

    @classmethod
    def placeholder(cls) -> Self:
        """get placeholder instance"""
        return cls("PH", "PH", WordType.PLACEHOLDER)

    @property
    def end(self) -> int:
        return self.offset + len(self.word_str)

    @property
    def isvirtual(self) -> bool:
        return self.type.isvirtual


WordList = list[Word]
"""Type alias: list[Word]"""


class Pt(Enum):
    """Enum: Parameter Type"""

    Num = 1
    Int = 2


@dataclass
class Operator:
    """Class: Operator"""

    w: int
    """weight"""
    operator: str
    """operator name"""
    func: Callable[[Any], Decimal] | None
    """function"""
    sig: list[Pt] = field(default_factory=list)
    """signature"""
    ffunc: Callable | None = None
    """format_func"""
    words: list[Word] = field(default_factory=list)
    """words"""

    @property
    def pc(self) -> int:
        return len(self.sig)


@dataclass
class Number:
    """Class: Number"""

    value: Decimal
    words: list[Word] = field(default_factory=list)
    strvalue: str = ""
    _is_placeholder = False

    @classmethod
    def placeholder(cls) -> Self:
        """get placehold number instance

        return:
            new expression func
        """
        return cls(Decimal(0))

    @property
    def isplaceholder(self) -> bool:
        return self._is_placeholder

    def __str__(self) -> str:
        if self.strvalue and not self.strvalue.isspace() and len(self.strvalue) > 0:
            return self.strvalue
        else:
            return str(self.value)


Register = Callable[[str], Decimal | None]
"""Type alias: Register"""


FUNC_SET = {"sum", "max", "min", "abs", "round", "hex", "oct"}


OPERATOR_SET = {"-", "+", "*", "/", "^"}
