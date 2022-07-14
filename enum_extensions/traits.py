from types import DynamicClassAttribute as dynamic_attribute
from typing import Any, ClassVar, Set, TypeVar

from enum_extensions.typing import is_same_type

__all__ = ("Trait", "Format", "Order", "Title")

T = TypeVar("T", bound="Trait")


class Trait:
    """Base type to derive traits from."""

    name: str
    value: Any
    title_name: str


class Format(Trait):
    """Enforces enumeration string formatting."""

    def __format__(self, specification: str) -> str:
        return str(self).__format__(specification)


class Order(Trait):
    """Implements ordering for enumerations."""

    def __lt__(self: T, other: T) -> bool:
        if is_same_type(other, self):
            return self.value < other.value

        return NotImplemented

    def __le__(self: T, other: T) -> bool:
        if is_same_type(other, self):
            return self.value <= other.value

        return NotImplemented

    def __gt__(self: T, other: T) -> bool:
        if is_same_type(other, self):
            return self.value > other.value

        return NotImplemented

    def __ge__(self: T, other: T) -> bool:
        if is_same_type(other, self):
            return self.value >= other.value

        return NotImplemented


class Title(Trait):
    """Allows handling abbreviations in titles."""

    ABBREVIATIONS: ClassVar[Set[str]] = set()

    @dynamic_attribute
    def title_name(self) -> str:  # type: ignore
        name = self.name

        if name in self.ABBREVIATIONS:
            return name

        return super().title_name
