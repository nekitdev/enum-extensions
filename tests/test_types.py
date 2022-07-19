from enum_extensions.types import Null, Singleton, is_not_null, is_null, null, singleton


def test_singleton_identity() -> None:
    assert Singleton() is Singleton()
    assert Null() is Null()


def test_is_null() -> None:
    assert is_null(null)
    assert not is_null(singleton)


def test_is_not_null() -> None:
    assert not is_not_null(null)
    assert is_not_null(singleton)
