import pickle
from builtins import hasattr as has_attribute
from math import sqrt
from typing import Any, Type, TypeVar

import pytest
from typing_extensions import Never

from enum_extensions.auto import auto
from enum_extensions.enums import Enum, IntEnum, StringEnum, find_data_type


class Empty(Enum):
    pass


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Season(Enum):
    WINTER = 1
    SPRING = 2
    SUMMER = 3
    AUTUMN = 4
    FALL = AUTUMN  # alias


class Constant(float, Enum):
    E = 2.718281828459045
    PI = 3.141592653589793
    TAU = 6.283185307179586


class Grade(IntEnum):
    A = 5
    B = 4
    C = 3
    D = 2
    F = 1


class JapaneseNumber(StringEnum):
    ONE = "ichi"
    TWO = "ni"
    THREE = "san"


class TestTypes:
    EMPTY = ((), object)
    WITH_DATA_TYPE = ((int, Enum), int)
    WITHOUT_DATA_TYPE = ((object, Enum), object)

    def test_find_data_type(self) -> None:
        for (bases, expected_type) in (self.EMPTY, self.WITH_DATA_TYPE, self.WITHOUT_DATA_TYPE):
            assert find_data_type(bases) is expected_type

    EXCESSIVE_TYPES = ((bool, int), (float, int), (bytes, str))

    def test_fail_on_excessive_types(self) -> None:
        for types in self.EXCESSIVE_TYPES:
            with pytest.raises(TypeError):
                find_data_type(types)


COLOR = "Color"

RED = "RED"
GREEN = "GREEN"
BLUE = "BLUE"

NAMES = (RED, GREEN, BLUE)

SPACE = " "
COMMA = ","

concat_space = SPACE.join
concat_comma = COMMA.join


class TestCreate:
    def test_create(self) -> None:
        class Color(Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()

    def test_create_using_string(self) -> None:
        Enum(COLOR, concat_space(NAMES))

    def test_create_using_commas(self) -> None:
        Enum(COLOR, concat_comma(NAMES))

    def test_create_using_sequence(self) -> None:
        Enum(COLOR, NAMES)

    def test_create_using_mapping(self) -> None:
        Enum(COLOR, {RED: auto(), GREEN: auto(), BLUE: auto()})

    def test_create_using_members(self) -> None:
        Enum(COLOR, RED=auto(), GREEN=auto(), BLUE=auto())

    def test_create_arguments(self) -> None:
        Enum.create(
            COLOR,
            start=1,
            module=__name__,
            qualified_name=COLOR,
            RED=auto(),
            GREEN=auto(),
            BLUE=auto(),
        )

    def test_invalid_definition(self) -> None:
        with pytest.raises(TypeError):
            class Broken(Enum, int):
                ...

    def test_break_on_extend_attempt(self) -> None:
        with pytest.raises(TypeError):
            class Extended(Color):
                ...

    def test_tuple_enum(self) -> None:
        origin = (0, 0)
        point = (1, 1)

        class Point(tuple, Enum):  # type: ignore
            ORIGIN = origin
            POINT = point

        assert Point.ORIGIN == origin
        assert Point.POINT == point

    def test_init(self) -> None:
        class Point(Enum):
            def __init__(self, x: int, y: int) -> None:
                self.x = x
                self.y = y

            @property
            def distance_from_origin(self) -> float:
                return sqrt(self.x * self.x + self.y * self.y)

            ORIGIN = (0, 0)

        assert Point.ORIGIN != (0, 0)

        assert not Point.ORIGIN.distance_from_origin

    def test_new(self) -> None:
        class IntEnum(int, Enum):
            __new__ = int.__new__  # idk

            ZERO = 0
            ONE = 1
            TWO = 2
            THREE = 3

    def test_not_hashable(self) -> None:
        class ListEnum(list, Enum):  # type: ignore
            EMPTY = []

        assert ListEnum([]) is ListEnum.EMPTY

    def test_derive(self) -> None:
        value = 42

        class DeriveEnum(Enum):
            @classmethod
            def derived(cls) -> int:
                return value

        class Derived(DeriveEnum):
            pass

        assert Derived.derived() == value


IGNORE = "IGNORE"


class TestSpecial:
    def test_enum_ignore(self) -> None:
        class Ignore(Enum, ignore=[IGNORE]):
            IGNORE = 13

        assert not has_attribute(Ignore, IGNORE)

    def test_enum_ignore_string(self) -> None:
        class Ignore(Enum, ignore=IGNORE):
            IGNORE = 42

        assert not has_attribute(Ignore, IGNORE)

    def test_enum_missing(self) -> None:
        C = TypeVar("C", bound="Color")

        class Color(Enum):
            UNKNOWN = 0
            RED = 1
            GREEN = 2
            BLUE = 3

            @classmethod
            def enum_missing(cls: Type[C], value: int) -> C:
                return cls.UNKNOWN

        assert Color(-1) is Color.UNKNOWN

    def test_invalid_enum_missing(self) -> None:
        class Invalid(Enum):
            @classmethod
            def enum_missing(cls, value: Any) -> Any:
                return value

        with pytest.raises(ValueError):
            Invalid(0)

    def test_failing_enum_missing(self) -> None:
        class Fails(Enum):
            @classmethod
            def enum_missing(cls, value: Any) -> Never:
                raise RuntimeError

        with pytest.raises(ValueError):
            Fails(0)

    def test_enum_start(self) -> None:
        class Value(Enum, start=0):
            ZERO = auto()

        assert Value(0) is Value.ZERO

    def test_enum_generate_next_value_missing(self) -> None:
        with pytest.raises(RuntimeError):
            class Missing(Enum):
                enum_generate_next_value = None

                MISSING = auto()

    def test_unknown(self) -> None:
        class Unknown(Enum, unknown=True):
            pass

        unknown = Unknown(0)

        assert unknown.__enum_name__ is None
        assert not unknown.__enum_value__


MRO = "mro"

SEASON = "Season"

SEASON_LENGTH = 4

WINTER_VALUE = 1
SPRING_VALUE = 2
SUMMER_VALUE = 3
AUTUMN_VALUE = 4

BROKEN_VALUE = 0

WINTER = "WINTER"
SPRING = "SPRING"
SUMMER = "SUMMER"
AUTUMN = "AUTUMN"

BROKEN = "BROKEN"

WINTER_NAME = "winter"
SPRING_NAME = "spring"
SUMMER_NAME = "summer"
AUTUMN_NAME = "autumn"

BROKEN_NAME = "broken"

BAR = "bar"


class TestEnum:
    def test_enum_to_enum(self) -> None:
        assert Season(Season.WINTER) is Season.WINTER

    def test_value_to_enum(self) -> None:
        assert Season(SPRING_VALUE) is Season.SPRING

        with pytest.raises(ValueError):
            Season(BROKEN_VALUE)

    def test_name_to_enum(self) -> None:
        assert Season[SUMMER] is Season.SUMMER

        with pytest.raises(KeyError):
            Season[BROKEN]

    def test_enum_from_name(self) -> None:
        assert Season.from_name(AUTUMN_NAME) is Season.AUTUMN

        with pytest.raises(KeyError):
            Season.from_name(BROKEN_NAME)

    def test_enum_from_value(self) -> None:
        assert Season.from_value(WINTER_VALUE) is Season.WINTER

        with pytest.raises(ValueError):
            Season.from_value(BROKEN_VALUE)

        assert Season.from_value(BROKEN_VALUE, default=SPRING_VALUE) is Season.SPRING

    def test_enum_from_data(self) -> None:
        assert Season.from_data(SUMMER_VALUE) is Season.from_data(SUMMER_NAME)

        with pytest.raises(ValueError):
            Season.from_data(BROKEN_NAME)

        assert Season.from_data(BROKEN_NAME, default=AUTUMN_NAME) is Season.AUTUMN

    def test_enum_name_title_value(self) -> None:
        assert Season.WINTER.name == WINTER
        assert Season.WINTER.title_name == WINTER.title()
        assert Season.WINTER.value == WINTER_VALUE

        with pytest.raises(AttributeError):
            Season.SPRING.name = BROKEN

        with pytest.raises(AttributeError):
            Season.SPRING.title_name = BROKEN.title()

        with pytest.raises(AttributeError):
            Season.SPRING.value = BROKEN_VALUE

    def test_change_member(self) -> None:
        with pytest.raises(AttributeError):
            Season.SPRING = BROKEN_VALUE

    def test_delete_attribute(self) -> None:
        class Foo(Enum):
            def bar(self) -> None:  # pragma: no cover
                pass

        assert has_attribute(Foo, BAR)

        del Foo.bar

        assert not has_attribute(Foo, BAR)

    def test_delete_member(self) -> None:
        with pytest.raises(AttributeError):
            del Season.SUMMER

    def test_iter_and_reverse(self) -> None:
        assert list(reversed(list(Season))) == list(reversed(Season))

    def test_class_bool(self) -> None:
        assert Season

    def test_member_bool(self) -> None:
        for member in JapaneseNumber:
            assert member

    def test_contains(self) -> None:
        class ListEnum(list, Enum):
            EMPTY = []

        assert [] in ListEnum

        assert Season.AUTUMN in Season

        assert WINTER_VALUE in Season

    def test_comparison(self) -> None:
        with pytest.raises(TypeError):
            Season.WINTER < Season.SUMMER

        assert Grade.A > Grade.F
        assert Constant.E < Constant.PI < Constant.TAU

        SeasonMimic = Enum(SEASON, (WINTER, SPRING, SUMMER, AUTUMN))

        assert Season.SPRING != SeasonMimic.SPRING

    def test_length(self) -> None:
        assert len(Season) == SEASON_LENGTH

    def test_aliases(self) -> None:
        assert Season.AUTUMN is Season.FALL

    def test_reassign_fail(self) -> None:
        with pytest.raises(ValueError):
            class Variable(Enum):
                variable = 13
                variable = 42

        with pytest.raises(ValueError):
            class OtherVariable(Enum):
                variable = 69  # type: ignore

                def variable(self) -> str:
                    ...

        with pytest.raises(ValueError):
            class AnotherVariable(Enum):
                def variable(self) -> str:
                    ...

                variable = 7  # type: ignore

    def test_invalid_member_names(self) -> None:
        with pytest.raises(ValueError):
            class InvalidName(Enum):
                mro = MRO

    def test_repr(self) -> None:
        assert repr(Grade) == "<enum `Grade`>"

    def test_member_str(self) -> None:
        assert str(Grade.A) == "Grade.A"

    def test_member_repr(self) -> None:
        assert repr(Grade.F) == "<Grade.F: 1>"

    def test_pickle(self) -> None:
        assert pickle.loads(pickle.dumps(Constant.TAU)) is Constant.TAU

    def test_hash(self) -> None:
        assert hash(Constant.E) == hash(Constant.E.name)


BLACK = "BLACK"


class TestMutation:
    def test_add_member(self) -> None:
        class Color(Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()

        black = Color.add_member(BLACK, 0)

        assert not black.value

    def test_update(self) -> None:
        class Color(Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()

        Color.update(BLACK=0, WHITE=auto())

        assert not Color.BLACK.value
        assert Color.WHITE.value

        with pytest.raises(ValueError):
            Color.update(BLACK=auto())
