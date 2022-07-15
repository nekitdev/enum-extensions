import pytest

from enum_extensions.auto import auto
from enum_extensions.enums import Enum
from enum_extensions.unique import unique


class Unique(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()


class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    R, G, B = RED, GREEN, BLUE


def test_unique() -> None:
    unique(Unique)


def test_not_unique() -> None:
    with pytest.raises(ValueError):
        unique(Color)
