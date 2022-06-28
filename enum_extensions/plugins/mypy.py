from typing import Final, Type

from mypy.plugin import Plugin

ENUM_BASES: Final = frozenset((
    "enum_extensions.enums.Enum",
    "enum_extensions.enums.IntEnum",
    "enum_extensions.enums.StringEnum",
    "enum_extensions.flags.Flag",
    "enum_extensions.flags.IntFlag",
))


class EnumExtensionsPlugin(Plugin):
    ...


def plugin(version: str) -> Type[EnumExtensionsPlugin]:
    return EnumExtensionsPlugin
