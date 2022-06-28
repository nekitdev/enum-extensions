from builtins import isinstance as is_instance
from typing import Generic, TypeVar, Union

from typing_extensions import TypeGuard

__all__ = ("Member", "NonMember", "member", "non_member", "is_member", "is_non_member")

T = TypeVar("T", covariant=True)
R = TypeVar("R")


class Member(Generic[T]):
    """Forces an item to become an [`Enum`][enum_extensions.enums.Enum] member."""

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        """The wrapped value to enforce enumeration membership of."""
        return self._value


class NonMember(Generic[T]):
    """Protects an item from becoming an [`Enum`][enum_extensions.enums.Enum] member."""

    def __init__(self, value: T) -> None:
        self._value = value

    @property
    def value(self) -> T:
        """The wrapped value to protect from becoming a member."""
        return self._value


def member(value: R) -> Member[R]:
    """Forces an item to become an [`Enum`][enum_extensions.enums.Enum] member.

    This is the same as `Member(value)`.

    Example:
        ```python
        def increment(value: int) -> int:
            return value + 1

        class Function(Enum):
            INCREMENT = member(increment)

        function = Function.INCREMENT  # <Function.INCREMENT: <function increment at ...>>
        ```

    Arguments:
        value: The value to enforce enumeration membership of.

    Returns:
        An instance of [`Member`][enum_extensions.members.Member] with the `value` wrapped.
    """

    return Member(value)


def non_member(value: R) -> NonMember[R]:
    """Protects an item from becoming an [`Enum`][enum_extensions.enums.Enum] member.

    This is the same as `NonMember(value)`.

    Example:
        ```python
        class Test:
            TEST = non_member(42)

        test = Test.TEST  # 42
        ```

    Arguments:
        value: The value to protect from becoming a member.

    Returns:
        An instance of [`NonMember`][enum_extensions.members.NonMember] with the `value` wrapped.
    """

    return NonMember(value)


MaybeMember = Union[Member[T], T]
MaybeNonMember = Union[NonMember[T], T]


def is_member(item: MaybeMember[T]) -> TypeGuard[Member[T]]:
    """Checks if an `item` is an instance of [`Member`][enum_extensions.members.Member].

    Example:
        ```python
        assert is_member(member(13))
        assert not is_member(13)
        ```

    Arguments:
        item: An instance to check.

    Returns:
        Whether an item is an instance of [`Member`][enum_extensions.members.Member].
    """
    return is_instance(item, Member)


def is_non_member(item: MaybeNonMember[T]) -> TypeGuard[NonMember[T]]:
    """Checks if an `item` is an instance of [`NonMember`][enum_extensions.members.NonMember].

    Example:
        ```python
        assert is_non_member(non_member(25))
        assert not is_non_member(25)
        ```

    Arguments:
        item: An instance to check.

    Returns:
        Whether an item is an instance of [`NonMember`][enum_extensions.members.NonMember].
    """
    return is_instance(item, NonMember)
