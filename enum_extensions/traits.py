from types import DynamicClassAttribute as dynamic_attribute
from typing import Any, ClassVar, Set, TypeVar
from typing_extensions import TypedDict

from enum_extensions.typing import is_same_type

__all__ = ("Trait", "FormatTrait", "JSONTrait", "OrderTrait", "TitleTrait")

T = TypeVar("T", bound="Trait")


class Trait:
    name: str
    value: Any
    title_name: str


class FormatTrait(Trait):
    def __format__(self, specification: str) -> str:
        return str(self).__format__(specification)


class EnumJSONDict(TypedDict):
    name: str
    value: Any


class JSONTrait(Trait):
    def __json__(self) -> EnumJSONDict:
        return EnumJSONDict(name=self.name, value=self.value)


class OrderTrait(Trait):
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


class TitleTrait(Trait):
    ABBREVIATIONS: ClassVar[Set[str]] = set()

    @dynamic_attribute
    def title_name(self) -> str:  # type: ignore
        name = self.name

        if name in self.ABBREVIATIONS:
            return name

        return super().title_name
