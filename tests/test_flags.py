import pytest

from enum_extensions.auto import auto
from enum_extensions.flags import CONFORM, KEEP, STRICT, Flag, IntFlag, is_flag, is_flag_member


class Permission(Flag, boundary=STRICT):
    N = 0
    X = 1
    W = 2
    R = 4


class Color(Flag, boundary=CONFORM):
    BLACK = 0
    RED = 1
    GREEN = 2
    BLUE = 4


class IntPermission(IntFlag, boundary=KEEP):
    R = 4
    W = 2
    X = 1


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
        class Color(Flag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()

        assert is_flag(Color)  # not sure where else to put this

    def test_create_using_string(self) -> None:
        Flag(COLOR, concat_space(NAMES))

    def test_create_using_commas(self) -> None:
        Flag(COLOR, concat_comma(NAMES))

    def test_create_using_sequence(self) -> None:
        Flag(COLOR, NAMES)

    def test_create_using_mapping(self) -> None:
        Flag(COLOR, {RED: auto(), GREEN: auto(), BLUE: auto()})

    def test_create_using_members(self) -> None:
        Flag(COLOR, RED=auto(), GREEN=auto(), BLUE=auto())

    def test_create_arguments(self) -> None:
        Flag.create(
            COLOR,
            start=1,
            module=__name__,
            qualified_name=COLOR,
            RED=auto(),
            GREEN=auto(),
            BLUE=auto(),
        )


N = "N"
XWR = "X, W, R"

R_NAME = "r"
W_NAME = "w"
X_NAME = "x"

Z_NAME = "z"

R_VALUE = 4
W_VALUE = 2
X_VALUE = 1


class TestFlag:
    INVALID = 0x10

    PERMISSIONS = (
        Permission.R | Permission.W | Permission.X,
        Permission.R | Permission.W,
        Permission.R | Permission.X,
        Permission.R,
        Permission.W | Permission.X,
        Permission.W,
        Permission.X,
        Permission.N,
    )

    STRING_MAPPING = {
        Permission.R: "Permission.R",
        Permission.W: "Permission.W",
        Permission.X: "Permission.X",
        Permission.N: "Permission.N",
        ~Permission.R: "Permission.X|W",
        ~Permission.W: "Permission.X|R",
        ~Permission.X: "Permission.W|R",
        ~Permission.N: "Permission.X|W|R",
    }

    def test_str(self) -> None:
        for member, string in self.STRING_MAPPING.items():
            assert str(member) == string

    REPRESENTATION_MAPPING = {
        Permission.R: "<Permission.R: 4>",
        Permission.W: "<Permission.W: 2>",
        Permission.X: "<Permission.X: 1>",
        Permission.N: "<Permission.N: 0>",
        ~Permission.R: "<Permission.X|W: 3>",
        ~Permission.W: "<Permission.X|R: 5>",
        ~Permission.X: "<Permission.W|R: 6>",
        ~Permission.N: "<Permission.X|W|R: 7>",
    }

    def test_repr(self) -> None:
        for member, representation in self.REPRESENTATION_MAPPING.items():
            assert repr(member) == representation

    def test_bool(self) -> None:
        assert Permission.R | Permission.W | Permission.X
        assert not Permission.N

    def test_title_name(self) -> None:
        assert Permission.N.title_name == N

        assert (Permission.R | Permission.W | Permission.X).title_name == XWR

    def test_or(self) -> None:
        for member in self.PERMISSIONS:
            for other in self.PERMISSIONS:
                assert member | other is Permission(member.value | other.value)

        with pytest.raises(TypeError):
            Permission.R | N

    def test_and(self) -> None:
        for member in self.PERMISSIONS:
            for other in self.PERMISSIONS:
                assert member & other is Permission(member.value & other.value)

        with pytest.raises(TypeError):
            Permission.W & N

    def test_xor(self) -> None:
        for member in self.PERMISSIONS:
            for other in self.PERMISSIONS:
                assert member ^ other is Permission(member.value ^ other.value)

        with pytest.raises(TypeError):
            Permission.X ^ N

    def test_invert(self) -> None:
        for member in self.PERMISSIONS:
            assert is_flag_member(~member)

            assert ~~member is member

    def test_contains(self) -> None:
        RW = Permission.R | Permission.W

        assert Permission.R in RW
        assert Permission.X not in RW

        assert Permission.N not in Permission.W

        with pytest.raises(TypeError):
            N in Permission.R

        with pytest.raises(TypeError):
            2 in Permission.W

    def test_decompose(self) -> None:
        decomposed = (Permission.X, Permission.W, Permission.R)
        composed = Permission.R | Permission.W | Permission.X

        assert tuple(composed) == decomposed

    def test_auto(self) -> None:
        class AutoFlag(Flag):
            ONE = auto()
            TWO = auto()
            FOUR = auto()

        values = (1, 2, 4)

        assert tuple(member.value for member in AutoFlag) == values

    def test_broken_auto(self) -> None:
        with pytest.raises(ValueError):
            class BrokenAuto(Flag):
                BROKEN = "broken"
                AUTO = auto()

    def test_from_names(self) -> None:
        assert (
            Permission.from_names(R_NAME, W_NAME, X_NAME)
            is Permission.R | Permission.W | Permission.X
        )

    def test_from_values(self) -> None:
        assert (
            Permission.from_values(R_VALUE, W_VALUE, X_VALUE)
            is Permission.R | Permission.W | Permission.X
        )

        with pytest.raises(ValueError):
            Permission.from_values(self.INVALID)

        assert (
            Permission.from_values(self.INVALID, R_VALUE, W_VALUE, X_VALUE, bound=False)
            is Permission.R | Permission.W | Permission.X
        )

    def test_from_data(self) -> None:
        with pytest.raises(ValueError):
            Permission.from_multiple_data(self.INVALID, Z_NAME)

        assert (
            Permission.from_multiple_data(self.INVALID, R_NAME, W_NAME, X_NAME, bound=False)
            is Permission.R | Permission.W | Permission.X
        )


class TestIntFlag:
    INT_PERMISSIONS = (
        IntPermission.R | IntPermission.W | IntPermission.X,
        IntPermission.R | IntPermission.W,
        IntPermission.R | IntPermission.X,
        IntPermission.R,
        IntPermission.W | IntPermission.X,
        IntPermission.W,
        IntPermission.X,
        IntPermission(0),
    )

    def test_type(self) -> None:
        assert IntPermission(0) >= 0  # inherited from `int`

    STRING_MAPPING = {
        IntPermission.R: "IntPermission.R",
        IntPermission.W: "IntPermission.W",
        IntPermission.X: "IntPermission.X",
        IntPermission(0): "IntPermission.0",
        IntPermission(8): "IntPermission.0x8",
        ~IntPermission.R: "IntPermission.W|X",
        ~IntPermission.W: "IntPermission.R|X",
        ~IntPermission.X: "IntPermission.R|W",
        ~IntPermission(0): "IntPermission.R|W|X",
        IntPermission(~8): "IntPermission.R|W|X",

        IntPermission(~8) | IntPermission(8): "IntPermission.R|W|X|0x8",
    }

    def test_str(self) -> None:
        for member, string in self.STRING_MAPPING.items():
            assert str(member) == string

    REPRESENTATION_MAPPING = {
        IntPermission.R: "<IntPermission.R: 4>",
        IntPermission.W: "<IntPermission.W: 2>",
        IntPermission.X: "<IntPermission.X: 1>",
        IntPermission(0): "<IntPermission.0: 0>",
        IntPermission(8): "<IntPermission.0x8: 8>",
        ~IntPermission.R: "<IntPermission.W|X: 3>",
        ~IntPermission.W: "<IntPermission.R|X: 5>",
        ~IntPermission.X: "<IntPermission.R|W: 6>",
        ~IntPermission(0): "<IntPermission.R|W|X: 7>",
        IntPermission(~8): "<IntPermission.R|W|X: 7>",

        IntPermission(~8) | IntPermission(8): "<IntPermission.R|W|X|0x8: 15>",
    }

    def test_repr(self) -> None:
        for member, representation in self.REPRESENTATION_MAPPING.items():
            assert repr(member) == representation

    def test_title_name(self) -> None:
        assert IntPermission(0).title_name == str(0)

    def test_fail_on_wrong_type(self) -> None:
        with pytest.raises(ValueError):
            IntPermission(4.2)

    def test_contains(self) -> None:
        assert IntPermission.R.value in IntPermission.R

        assert IntPermission.W in (IntPermission.R | IntPermission.W | IntPermission.X)
        assert IntPermission.X not in (IntPermission.R | IntPermission.W)

        assert 0 not in IntPermission(0)  # special

        with pytest.raises(TypeError):
            N in IntPermission(0)

    def test_or(self) -> None:
        for member in self.INT_PERMISSIONS:
            for other in self.INT_PERMISSIONS:
                assert member | other is IntPermission(member.value | other.value)

                assert member | other.value is IntPermission(member.value | other.value)
                assert member.value | other is IntPermission(member.value | other.value)

        with pytest.raises(TypeError):
            IntPermission(0) | N

    def test_and(self) -> None:
        for member in self.INT_PERMISSIONS:
            for other in self.INT_PERMISSIONS:
                assert member & other is IntPermission(member.value & other.value)

                assert member & other.value is IntPermission(member.value & other.value)
                assert member.value & other is IntPermission(member.value & other.value)

        with pytest.raises(TypeError):
            IntPermission(0) & N

    def test_xor(self) -> None:
        for member in self.INT_PERMISSIONS:
            for other in self.INT_PERMISSIONS:
                assert member ^ other is IntPermission(member.value ^ other.value)

                assert member ^ other.value is IntPermission(member.value ^ other.value)
                assert member.value ^ other is IntPermission(member.value ^ other.value)

        with pytest.raises(TypeError):
            IntPermission(0) ^ N

    def test_invert(self) -> None:
        for member in self.INT_PERMISSIONS:
            assert is_flag_member(member)

            assert ~member is IntPermission(~member.value)

            assert ~~member is member


RWX = "R, W, X"
RWX_NOT_COVERED = "R, W, X ({} not covered)"


class TestFlagBoundary:
    INVALID = 0x10

    def test_strict_boundary(self) -> None:
        with pytest.raises(ValueError):
            Permission(self.INVALID)

    def test_conform_boundary(self) -> None:
        assert Color(self.INVALID) is Color.BLACK

    def test_keep_boundary(self) -> None:
        RWX = IntPermission.R | IntPermission.W | IntPermission.X

        assert (RWX | self.INVALID) is IntPermission(RWX.value | self.INVALID)

    def test_keep_boundary_title_name(self) -> None:
        RWX = IntPermission.R | IntPermission.W | IntPermission.X

        INVALID = IntPermission(self.INVALID)

        assert RWX.title_name == "R, W, X"

        assert INVALID.title_name == hex(self.INVALID)

        assert (RWX | INVALID).title_name == RWX_NOT_COVERED.format(hex(self.INVALID))

    def test_invalid_definition(self) -> None:
        with pytest.raises(TypeError):
            class Color(Flag):
                RED = 1  # we define one color
                # BLUE = 4  # and we do not define another color (commented out on purpose)
                MAGENTA = 1 | 4  # but use their combination, which is impossible unless KEEP

    def test_unknown_values(self) -> None:
        class Color(Flag, boundary=STRICT):
            RED = 1
            # BLUE = 4  # again, not defined (commented out on purpose)

        with pytest.raises(ValueError):
            MAGENTA = Color(1 | 4)  # attempt to initialize


class TestUpdate:
    def test_update_works(self) -> None:
        value = 1 | 2 | 4

        Color.update(WHITE=value)

        assert Color(value) == Color.WHITE

    def test_update_with_auto(self) -> None:
        class Color(Flag):
            pass

        Color.update(RED=auto(), GREEN=auto(), BLUE=auto())

        assert Color.BLUE.value == 4

    def test_error_if_exists(self) -> None:
        with pytest.raises(ValueError):
            Color.update(BLACK=0)

    def test_flag_update(self) -> None:
        class NewPermission(Flag):
            R = 4
            W = 2
            X = 1

        RWX = NewPermission.R | NewPermission.W | NewPermission.X

        assert repr(RWX) == "<NewPermission.R|W|X: 7>"

        NewPermission.update(N=0, WX=3, RX=5, RW=6, RWX=7)

        assert repr(RWX) == "<NewPermission.RWX: 7>"

        assert NewPermission(0).name == N
