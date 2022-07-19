import pickle

import pytest

from enum_extensions.utils import (
    is_descriptor,
    is_double_under_name,
    make_namespace_unpicklable,
    make_type_unpicklable,
)

DESCRIPTOR = property()
NON_DESCRIPTOR = 42


def test_is_descriptor() -> None:
    assert is_descriptor(DESCRIPTOR)
    assert not is_descriptor(NON_DESCRIPTOR)


DOUBLE_UNDER = "__name__"
NOT_DOUBLE_UNDER = (
    "_",
    "__",
    "___",
    "____",
    "_____",
    "name",
    "_name",
    "name_",
    "__name",
    "name__",
    "_name_",
    "__name_",
    "_name__",
    "___name__",
    "__name___",
    "___name___",
)


def test_is_double_under_name() -> None:
    assert is_double_under_name(DOUBLE_UNDER)

    for name in NOT_DOUBLE_UNDER:
        assert not is_double_under_name(name)


class Type:
    pass


def test_make_type_unpicklable() -> None:
    instance = Type()

    pickle.dumps(instance)  # should work

    make_type_unpicklable(Type)

    with pytest.raises(TypeError):
        pickle.dumps(instance)


def test_make_namespace_unpicklable() -> None:
    namespace = {}

    make_namespace_unpicklable(namespace)

    class Type:
        vars().update(namespace)

    instance = Type()

    with pytest.raises(TypeError):
        pickle.dumps(instance)
