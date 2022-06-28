from builtins import hasattr as has_attribute
from builtins import setattr as set_attribute
from itertools import chain
from typing import Any, Iterable, Iterator, Tuple, Type, TypeVar

from typing_extensions import Never, TypeVarTuple, Unpack

from enum_extensions.constants import (
    DELETE,
    DOUBLE_UNDER,
    GET,
    MODULE,
    REDUCE,
    SET,
    TWO,
    UNDER,
    UNKNOWN,
)
from enum_extensions.string import tick
from enum_extensions.typing import Namespace, get_name

__all__ = (
    "get_frame",
    "create_annotations_type",
    "is_descriptor",
    "is_double_under_name",
    "make_namespace_unpicklable",
    "make_type_unpicklable",
    "tuple_args",
    "prepend",
)

try:
    from sys import _getframe as get_frame

except ImportError:  # pragma: no cover
    from types import FrameType as Frame

    class GetFrame(BaseException):
        pass

    NO_TRACEBACK = "no traceback to get the frame from"
    NO_CALLER_FRAME = "can not get the caller frame"
    CALL_STACK_NOT_DEEP_ENOUGH = "call stack is not deep enough"

    def get_frame(depth: int = 0) -> Frame:
        try:
            raise GetFrame()

        except GetFrame as error:
            traceback = error.__traceback__

            if traceback is None:
                raise ValueError(NO_TRACEBACK) from None

            current = traceback.tb_frame

            frame = current.f_back

            if frame is None:
                raise ValueError(NO_CALLER_FRAME) from None

            for _ in range(depth):
                frame = frame.f_back

                if frame is None:
                    raise ValueError(CALL_STACK_NOT_DEEP_ENOUGH) from None

            return frame


T = TypeVar("T")


def is_descriptor(item: Any) -> bool:
    return has_attribute(item, GET) or has_attribute(item, SET) or has_attribute(item, DELETE)


def is_double_under_name(name: str) -> bool:
    under = UNDER
    double_under = DOUBLE_UNDER
    two = TWO
    four = two + two  # heh

    return (
        len(name) > four
        and name[:two] == double_under
        and name[-two:] == double_under
        and name[two] != under
        and name[~two] != under
    )


NOT_PICKLABLE = "{} instance is not picklable"


def make_namespace_unpicklable(namespace: Namespace) -> None:
    def error_on_reduce(instance: T, protocol: int) -> Never:
        raise TypeError(NOT_PICKLABLE.format(tick(get_name(type(instance)))))

    namespace[REDUCE] = error_on_reduce
    namespace[MODULE] = UNKNOWN


def make_type_unpicklable(type: Type[T]) -> None:
    def error_on_reduce(instance: T, protocol: int) -> Never:
        raise TypeError(NOT_PICKLABLE.format(tick(get_name(type))))

    set_attribute(type, REDUCE, error_on_reduce)
    set_attribute(type, MODULE, UNKNOWN)


Args = TypeVarTuple("Args")


def tuple_args(*args: Unpack[Args]) -> Tuple[Unpack[Args]]:
    return args


def prepend(item: T, iterable: Iterable[T]) -> Iterator[T]:
    return chain(tuple_args(item), iterable)
