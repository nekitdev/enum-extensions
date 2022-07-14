import pytest

from enum_extensions.enums import Enum, IntEnum
from enum_extensions.members import non_member
from enum_extensions.traits import Format, Order, Title


class Shade(Enum):
    BLACK = 0
    WHITE = 100


class IntShade(IntEnum):
    BLACK = 0
    WHITE = 100


class Ordered(Order, Enum):
    BLACK = 0
    WHITE = 100


def test_no_order() -> None:
    with pytest.raises(TypeError):
        Shade.BLACK < Shade.WHITE

    with pytest.raises(TypeError):
        Shade.WHITE > Shade.BLACK

    with pytest.raises(TypeError):
        Shade.BLACK <= Shade.BLACK

    with pytest.raises(TypeError):
        Shade.WHITE >= Shade.WHITE


def test_order() -> None:
    assert Ordered.BLACK < Ordered.WHITE
    assert Ordered.WHITE > Ordered.BLACK
    assert Ordered.BLACK <= Ordered.BLACK
    assert Ordered.WHITE >= Ordered.WHITE


class OtherOrdered(Order, Enum):
    BLACK = 0
    WHITE = 100


def test_other_order() -> None:
    with pytest.raises(TypeError):
        Ordered.BLACK < OtherOrdered.WHITE

    with pytest.raises(TypeError):
        Ordered.WHITE > OtherOrdered.BLACK

    with pytest.raises(TypeError):
        Ordered.BLACK <= OtherOrdered.BLACK

    with pytest.raises(TypeError):
        Ordered.WHITE >= OtherOrdered.WHITE


BLACK_NAME = "BLACK"
WHITE_NAME = "WHITE"

GRAY_TITLE = "Gray"

BLACK_TITLE = "Black"
WHITE_TITLE = "White"


class Titled(Title, Enum):
    ABBREVIATIONS = non_member({BLACK_NAME, WHITE_NAME})

    BLACK = 0
    GRAY = 50
    WHITE = 100


def test_no_title() -> None:
    assert Shade.BLACK.title_name == BLACK_TITLE
    assert Shade.WHITE.title_name == WHITE_TITLE


def test_title() -> None:
    assert Titled.BLACK.title_name == BLACK_NAME
    assert Titled.WHITE.title_name == WHITE_NAME

    assert Titled.GRAY.title_name == GRAY_TITLE


BLACK_INT_FORMAT = str(0)
WHITE_INT_FORMAT = str(100)

BLACK_NORMAL_FORMAT = "Shade.BLACK"
WHITE_NORMAL_FORMAT = "Shade.WHITE"

BLACK_FORMAT = "Formatted.BLACK"
WHITE_FORMAT = "Formatted.WHITE"


class Formatted(Format, IntEnum):
    BLACK = 0
    WHITE = 100


def test_no_format() -> None:
    assert format(Shade.BLACK) == BLACK_NORMAL_FORMAT
    assert format(Shade.WHITE) == WHITE_NORMAL_FORMAT

    assert format(IntShade.BLACK) == BLACK_INT_FORMAT
    assert format(IntShade.WHITE) == WHITE_INT_FORMAT


def test_format() -> None:
    assert format(Formatted.BLACK) == BLACK_FORMAT
    assert format(Formatted.WHITE) == WHITE_FORMAT
