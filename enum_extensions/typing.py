from builtins import hasattr as has_attribute
from builtins import isinstance as is_instance
from typing import Any, Callable, Dict, Iterable, Mapping, Tuple, Type, TypeVar, Union

from typing_extensions import Protocol, TypeGuard

from enum_extensions.constants import NAME

__all__ = (
    "AnyType",
    "StringMapping",
    "StringPairs",
    "Pairs",
    "StringDict",
    "Namespace",
    "MaybeIterable",
    "Names",
    "EmptyTuple",
    "DynamicTuple",
    "DynamicCallable",
    "Nullary",
    "Unary",
    "Binary",
    "Ternary",
    "Quaternary",
    "Named",
    "get_name",
    "is_named",
    "is_int",
    "is_string",
    "is_same_type",
    "is_mapping",
    "is_tuple",
)

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
R = TypeVar("R")

AnyType = Type[Any]

StringMapping = Mapping[str, T]

Pairs = Iterable[Tuple[T, U]]

StringPairs = Pairs[str, T]

StringDict = Dict[str, T]

Namespace = StringDict[Any]

MaybeIterable = Union[T, Iterable[T]]
MaybeMapping = Union[Mapping[T, U], V]

Names = Union[MaybeIterable[str], StringPairs[Any], StringMapping[Any]]

EmptyTuple = Tuple[()]

DynamicTuple = Tuple[T, ...]

DynamicCallable = Callable[..., R]

Nullary = Callable[[], R]
Unary = Callable[[T], R]
Binary = Callable[[T, U], R]
Ternary = Callable[[T, U, V], R]
Quaternary = Callable[[T, U, V, W], R]


class Named(Protocol):
    __name__: str


def get_name(item: Named) -> str:
    return item.__name__


def is_named(item: Any) -> TypeGuard[Named]:  # pragma: no cover  # not used anywhere in the code
    return has_attribute(item, NAME)


def is_int(item: Any) -> TypeGuard[int]:
    return is_instance(item, int)


def is_string(item: Any) -> TypeGuard[str]:
    return is_instance(item, str)


def is_same_type(item: Any, value: T) -> TypeGuard[T]:
    return type(item) is type(value)


def is_mapping(item: MaybeMapping[T, U, V]) -> TypeGuard[Mapping[T, U]]:
    return is_instance(item, Mapping)


def is_tuple(item: Any) -> TypeGuard[DynamicTuple[Any]]:
    return is_instance(item, tuple)
