from typing import Type as TypingType

from mypy.plugin import Plugin


class EnumExtensionsPlugin(Plugin):
    ...


def plugin(version: str) -> TypingType[EnumExtensionsPlugin]
    return EnumExtensionsPlugin
