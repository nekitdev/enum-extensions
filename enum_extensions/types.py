from threading import Lock
from typing import Any, Type, TypeVar, Union

from typing_extensions import TypeGuard

from enum_extensions.typing import get_name

__all__ = (
    "SingletonType",
    "Singleton",
    "singleton",
    "Null",
    "Nullable",
    "null",
    "is_null",
    "is_not_null",
)


S = TypeVar("S")
T = TypeVar("T")


class SingletonType(type):
    _INSTANCES = {}  # type: ignore
    _LOCK = Lock()

    def __call__(cls: Type[S], *args: Any, **kwargs: Any) -> S:
        instances = cls._INSTANCES
        lock = cls._LOCK

        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = super().__call__(*args, **kwargs)

        return instances[cls]


class Singleton(metaclass=SingletonType):
    def __repr__(self) -> str:
        return get_name(type(self))


singleton = Singleton()


class Null(Singleton):
    pass


null = Null()

Nullable = Union[T, Null]


def is_null(item: Nullable[T]) -> TypeGuard[Null]:
    return item is null


def is_not_null(item: Nullable[T]) -> TypeGuard[T]:
    return item is not null
