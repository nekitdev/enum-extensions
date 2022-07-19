from typing import TypeVar

from enum_extensions.enums import Enum, is_enum_member
from enum_extensions.members import member, non_member

T = TypeVar("T")


def identity(value: T) -> T:
    return value


def test_member() -> None:
    class Function(Enum):
        IDENTITY = member(identity)

    assert is_enum_member(Function.IDENTITY)

    class NotFunction(Enum):
        IDENTITY = identity

    assert not is_enum_member(NotFunction.IDENTITY)


def test_non_member() -> None:
    class NotValue(Enum):
        ZERO = non_member(0)

    assert not is_enum_member(NotValue.ZERO)

    class Value(Enum):
        ZERO = 0

    assert is_enum_member(Value.ZERO)
