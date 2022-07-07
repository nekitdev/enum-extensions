from typing import Iterator, Tuple, Type, TypeVar

from enum_extensions.enums import Enum
from enum_extensions.flags import Flag
from enum_extensions.string import concat_comma_space, tick
from enum_extensions.typing import get_name

__all__ = ("unique",)

ET = TypeVar("ET", bound="Type[Enum]")
FT = TypeVar("FT", bound="Type[Flag]")


MAPPING = "{} -> {}"
mapping = MAPPING.format

ALIASES_FOUND = "aliases found in {}: {}"


def unique(enum: ET) -> ET:
    duplicates = concat_comma_space(
        mapping(tick(name), tick(member_name)) for name, member_name in find_duplicates(enum)
    )

    if duplicates:
        raise ValueError(ALIASES_FOUND.format(tick(get_name(enum)), duplicates))

    return enum


def find_duplicates(enum: ET) -> Iterator[Tuple[str, str]]:
    for name, member in enum.members.items():
        if name != member.name:
            yield (name, member.name)
