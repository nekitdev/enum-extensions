from enum_extensions.utils import is_descriptor, is_double_under_name

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
