import pytest

from enum_extensions.enums import Enum, IntEnum
from enum_extensions.members import non_member
from enum_extensions.traits import FormatTrait, OrderTrait, TitleTrait


class Shade(Enum):
    BLACK = 0
    WHITE = 100


class IntShade(IntEnum):
    BLACK = 0
    WHITE = 100


class Order(OrderTrait, Enum):
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
    assert Order.BLACK < Order.WHITE
    assert Order.WHITE > Order.BLACK
    assert Order.BLACK <= Order.BLACK
    assert Order.WHITE >= Order.WHITE


class OtherOrder(OrderTrait, Enum):
    BLACK = 0
    WHITE = 100


def test_other_order() -> None:
    with pytest.raises(TypeError):
        Order.BLACK < OtherOrder.WHITE

    with pytest.raises(TypeError):
        Order.WHITE > OtherOrder.BLACK

    with pytest.raises(TypeError):
        Order.BLACK <= OtherOrder.BLACK

    with pytest.raises(TypeError):
        Order.WHITE >= OtherOrder.WHITE


BLACK_NAME = "BLACK"
WHITE_NAME = "WHITE"

GRAY_TITLE = "Gray"

BLACK_TITLE = "Black"
WHITE_TITLE = "White"


class Title(TitleTrait, Enum):
    ABBREVIATIONS = non_member({BLACK_NAME, WHITE_NAME})

    BLACK = 0
    GRAY = 50
    WHITE = 100


def test_no_title() -> None:
    assert Shade.BLACK.title_name == BLACK_TITLE
    assert Shade.WHITE.title_name == WHITE_TITLE


def test_title() -> None:
    assert Title.BLACK.title_name == BLACK_NAME
    assert Title.WHITE.title_name == WHITE_NAME

    assert Title.GRAY.title_name == GRAY_TITLE


BLACK_INT_FORMAT = str(0)
WHITE_INT_FORMAT = str(100)

BLACK_NORMAL_FORMAT = "Shade.BLACK"
WHITE_NORMAL_FORMAT = "Shade.WHITE"

BLACK_FORMAT = "Format.BLACK"
WHITE_FORMAT = "Format.WHITE"


class Format(FormatTrait, IntEnum):
    BLACK = 0
    WHITE = 100


def test_no_format() -> None:
    assert format(Shade.BLACK) == BLACK_NORMAL_FORMAT
    assert format(Shade.WHITE) == WHITE_NORMAL_FORMAT

    assert format(IntShade.BLACK) == BLACK_INT_FORMAT
    assert format(IntShade.WHITE) == WHITE_INT_FORMAT


def test_format() -> None:
    assert format(Format.BLACK) == BLACK_FORMAT
    assert format(Format.WHITE) == WHITE_FORMAT
