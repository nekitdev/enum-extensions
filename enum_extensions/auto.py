from builtins import isinstance as is_instance
from typing import Any, Generic, Type, TypeVar, Union, overload

from typing_extensions import TypeGuard

from enum_extensions.types import Nullable, null

__all__ = ("AnyAuto", "Auto", "MaybeAuto", "auto", "is_auto")

T = TypeVar("T", covariant=True)


class Auto(Generic[T]):
    """Instances are replaced with an appropriate generated value
    in [`Enum`][enum_extensions.enums.Enum] classes.
    """

    def __init__(self, value: Nullable[T] = null) -> None:
        self._value = value

    @property
    def value(self) -> Nullable[T]:
        """The wrapped value."""

        return self._value

    @value.setter
    def value(self, value: Nullable[T]) -> None:
        """The wrapped value."""

        self._value = value


AnyAuto = Auto[Any]

MaybeAuto = Union[Auto[T], T]

A = TypeVar("A", bound=AnyAuto)


@overload
def auto() -> AnyAuto:
    ...


@overload
def auto(auto_type: Type[A]) -> A:
    ...


def auto(auto_type: Type[AnyAuto] = AnyAuto) -> AnyAuto:
    """Creates an [`Auto`][enum_extensions.auto.Auto] instance.

    Example:
        ```python
        class Test(Enum, start=13):
            TEST = auto()  # <- used here

        test = Test.TEST  # <Test.TEST: 13> <- an appropriate generated value
        ```

    This function simply calls `auto_type()` to create an appropriate instance.

    Arguments:
        auto_type: The [`Auto`][enum_extensions.auto.Auto] type to use.

    Returns:
        A newly created [`Auto`][enum_extensions.auto.Auto] instance.
    """
    return auto_type()


def is_auto(item: MaybeAuto[T]) -> TypeGuard[Auto[T]]:
    """Checks if an `item` is an instance of [`Auto`][enum_extensions.auto.Auto].

    Example:
        ```python
        assert is_auto(auto())
        assert not is_auto(42)
        ```

    Arguments:
        item: An instance to check.

    Returns:
        Whether an item is an instance of [`Auto`][enum_extensions.auto.Auto].
    """
    return is_instance(item, Auto)
