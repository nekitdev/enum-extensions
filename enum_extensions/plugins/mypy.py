from typing import Type

from mypy.plugin import Plugin


class EnumExtensionsPlugin(Plugin):
    ...


def plugin(version: str) -> Type[EnumExtensionsPlugin]:
    return EnumExtensionsPlugin
