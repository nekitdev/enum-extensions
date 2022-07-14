from typing import Type as PythonType

from mypy.plugin import Plugin


class EnumExtensionsPlugin(Plugin):
    ...


def plugin(version: str) -> PythonType[EnumExtensionsPlugin]:
    return EnumExtensionsPlugin
