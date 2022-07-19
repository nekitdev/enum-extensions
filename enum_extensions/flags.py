from __future__ import annotations

from builtins import getattr as get_attribute
from builtins import isinstance as is_instance
from builtins import issubclass as is_subclass
from builtins import type as standard_type
from types import DynamicClassAttribute as dynamic_attribute
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import TypeGuard

from enum_extensions.auto import auto
from enum_extensions.bits import bin, bit_at, bit_count, bit_mask, is_single_bit, iter_bits
from enum_extensions.constants import (
    BOUNDARY_PRIVATE,
    COMMA,
    DIRECT_CALLER,
    MODULE,
    NAME,
    NESTED_CALLER,
    QUALIFIED_NAME,
    SPACE,
)
from enum_extensions.enums import Enum, EnumDict, EnumType, StringEnum, find_enum_type
from enum_extensions.string import concat_comma_space, concat_pipe, create_title, tick
from enum_extensions.types import is_not_null, null
from enum_extensions.typing import (
    AnyType,
    DynamicTuple,
    MaybeIterable,
    Names,
    StringDict,
    get_name,
    is_int,
    is_mapping,
    is_same_type,
    is_string,
)
from enum_extensions.utils import get_frame, make_namespace_unpicklable, prepend

__all__ = ("FlagBoundary", "FlagType", "Flag", "IntFlag", "is_flag", "is_flag_member")

F = TypeVar("F")
FT = TypeVar("FT")

FlagT = TypeVar("FlagT", bound="Flag")


class FlagBoundary(StringEnum):
    """Controls how *out-of-range* values are handled in
    [`Flag`][enum_extensions.flags.Flag] types.
    """

    STRICT = auto()
    """*Out-of-range* values cause [`ValueError`][ValueError].
    This is the default for [`Flag`][enum_extensions.flags.Flag].

    Example:
        ```python
        from enum_extensions import STRICT, Flag

        class StrictFlag(Flag, boundary=STRICT):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        ```

        ```python
        >>> StrictFlag((1 << 2) + (1 << 4))

        Traceback (most recent call last):
          ...
        ValueError: invalid value 0x14 in `StrictFlag`:
            given 0b0 10100
          allowed 0b0 00111
        ```
    """

    CONFORM = auto()
    """*Out-of-range* values have invalid values removed, leaving a valid
    [`Flag`][enum_extensions.flags.Flag] member.

    Example:
        ```python
        from enum_extensions import CONFORM, Flag

        class ConformFlag(Flag, boundary=CONFORM):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        ```

        ```python
        >>> ConformFlag((1 << 2) + (1 << 4))
        <ConformFlag.BLUE: 4>
        ```
    """

    KEEP = auto()
    """*Out-of-range* values are kept along with the
    [`Flag`][enum_extensions.flags.Flag] membership.
    This is the default for [`IntFlag`][enum_extensions.flags.IntFlag].

    Example:
        ```python
        from enum_extensions import KEEP, Flag

        class KeepFlag(Flag, boundary=KEEP):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        ```

        ```python
        >>> KeepFlag((1 << 2) + (1 << 4))
        <KeepFlag.BLUE|0x10: 4>
        ```
    """


STRICT, CONFORM, KEEP = FlagBoundary

INVALID_FLAG_VALUE = "invalid flag value: {}"


def strict_bit_next_value(
    name: str, start: Optional[int], count: int, values: Sequence[int]
) -> int:
    if start is None:
        start = 1

    for value in reversed(values):
        try:
            return bit_at(value.bit_length())

        except AttributeError:
            raise ValueError(INVALID_FLAG_VALUE.format(repr(value)))

    else:
        return start


INVALID_FLAG = "invalid flag {}; missing values: {}"
INVALID_VALUE = "{} is not a valid {}"
INVALID_BITS = """
invalid value {} in {}:
    given {}
  allowed {}
""".strip()

UNKNOWN_BOUNDARY = "unknown flag boundary: {}"
UNKNOWN_VALUES = "{}({}) -> unknown values {} [{}]"

FLAG_REPRESENTATION = "<flag {}>"

QUALIFIED_NAME_STRING = "{}.{}"


class FlagType(EnumType):
    _member_values: List[int]
    _member_mapping: StringDict[Flag]  # type: ignore
    _value_mapping: Dict[int, Flag]  # type: ignore

    _flag_mask: int
    _full_mask: int

    _bit_length: int

    _boundary: FlagBoundary

    def __new__(
        cls: Type[FT],
        flag_name: str,
        bases: DynamicTuple[AnyType],
        namespace: EnumDict,
        *,
        ignore: Optional[MaybeIterable[str]] = None,
        start: Optional[int] = None,
        boundary: Optional[FlagBoundary] = None,
        **kwargs: Any,
    ) -> FT:
        new_flag_type = super().__new__(
            cls, flag_name, bases, namespace, ignore=ignore, start=start, flag=True
        )

        if boundary is None:
            boundary = get_attribute(new_flag_type, BOUNDARY_PRIVATE, STRICT)

        flag_mask = 0

        for value in new_flag_type._member_values:
            flag_mask |= value

        bit_length = flag_mask.bit_length()

        full_mask = bit_mask(bit_length)

        new_flag_type._flag_mask = flag_mask
        new_flag_type._full_mask = full_mask

        new_flag_type._bit_length = bit_length

        new_flag_type._boundary = boundary

        new_flag_type._modify_mask_and_iter()

        return new_flag_type

    def _modify_mask_and_iter(self) -> None:
        single_bit_total = 0
        multi_bit_total = 0

        for flag in self._member_mapping.values():
            value = flag.__enum_value__

            if is_single_bit(value):
                single_bit_total |= value

            else:
                multi_bit_total |= value  # multi-bit flags are considered aliases

        if self._boundary is not KEEP:
            missed = multi_bit_total & ~single_bit_total

            if missed:
                raise TypeError(INVALID_FLAG.format(tick(get_name(self)), hex(missed)))

        self._flag_mask = single_bit_total

        flag_list = [flag.__enum_value__ for flag in self]

        if sorted(flag_list) != flag_list:
            # definition order is not the same as increasing value order
            self._iter_member = self._iter_member_by_defintion

    @overload
    def __call__(self: Type[F], value: Any) -> F:
        ...

    @overload
    def __call__(
        self: FT,
        value: str,
        names: Optional[Names] = ...,
        *,
        module: Optional[str] = ...,
        qualified_name: Optional[str] = ...,
        type: Optional[AnyType] = ...,
        start: Optional[Any] = ...,
        boundary: Optional[FlagBoundary] = ...,
        **members: Any,
    ) -> FT:
        ...

    def __call__(
        self: Type[F],
        value: Any,
        names: Optional[Names] = None,
        *,
        module: Optional[str] = None,
        qualified_name: Optional[str] = None,
        type: Optional[AnyType] = None,
        start: Optional[Any] = None,
        boundary: Optional[FlagBoundary] = None,
        **members: Any,
    ) -> Union[F, Type[F]]:
        """Looks up an existing member or creates a new flag.

        Example:

            Creation:

            ```python
            Color = Flag("Color", RED=1, GREEN=2, BLUE=4)
            ```

            Value lookup:

            ```python
            blue = Color(4)  # <Color.BLUE: 4>
            ```

        Arguments:
            value: The value to search for or the name of the
                new [`Flag`][enum_extensions.flags.Flag] to create.
            names: The names/values of the new flag members.
            module: The name of the module the [`Flag`][enum_extensions.flags.Flag] is created in.
            qualified_name: The actual location in the module where the flag can be found.
            type: A data type of the new [`Flag`][enum_extensions.flags.Flag].
            start: The initial value of the new flag (used by [`auto`][enum_extensions.auto.auto]).
            boundary: The [`FlagBoundary`][enum_extensions.flags.FlagBoundary] to use.
                [`None`] means it should be inherited. The default boundary in the end is
                [`STRICT`][enum_extensions.flags.FlagBoundary.STRICT].
            **members: A `name -> value` mapping of [`Flag`][enum_extensions.flags.Flag] members.

        Raises:
            ValueError: The member was not found.
            ValueError: The name is already used by another member.

        Returns:
            A newly created [`Flag`][enum_extensions.flags.Flag] type or a member found.
        """

        if names or module or qualified_name or type or start or boundary or members:
            return self.create(
                value,
                names,
                module=module,
                qualified_name=qualified_name,
                type=type,
                start=start,
                boundary=boundary,
                direct_call=False,
                **members,
            )

        return self.__new__(self, value)

    def create(
        self: FT,
        flag_name: str,
        names: Optional[Names] = None,
        *,
        module: Optional[str] = None,
        qualified_name: Optional[str] = None,
        type: Optional[AnyType] = None,
        start: Optional[Any] = None,
        boundary: Optional[FlagBoundary] = None,
        direct_call: bool = True,
        **members: Any,
    ) -> FT:
        """Creates a new flag.

        Example:

            ```python
            Color = Flag("Color", ("RED", "GREEN", "BLUE"))
            ```

        Arguments:
            flag_name: The name of the new [`Flag`][enum_extensions.flags.Flag] to create.
            names: The names/values of the new flag members.
            module: The name of the module the [`Flag`][enum_extensions.flags.Flag] is created in.
            qualified_name: The actual location in the module where the flag can be found.
            type: A data type of the new [`Flag`][enum_extensions.flags.Flag].
            start: The initial value of the new flag (used by [`auto`][enum_extensions.auto.auto]).
            boundary: The [`FlagBoundary`][enum_extensions.flags.FlagBoundary] to use.
                [`None`][None] means it should be inherited. The default boundary in the end is
                [`STRICT`][enum_extensions.flags.FlagBoundary.STRICT].
            direct_call: Controls if the function is called directly or not.
                This argument should be used with caution.
            **members: A `name -> value` mapping of [`Flag`][enum_extensions.flags.Flag] members.

        Raises:
            ValueError: The name is already used by another member.

        Returns:
            A newly created [`Flag`][enum_extensions.flags.Flag] type.
        """
        meta = standard_type(self)

        bases = (self,) if type is None else (type, self)

        enum_type = find_enum_type(bases)

        namespace = meta.__prepare__(flag_name, bases, start=start, boundary=boundary)

        if names is not None:
            # special processing needed for strings
            if is_string(names):
                names = names.replace(COMMA, SPACE).strip().split()

            if is_mapping(names):
                namespace.update(names)

            else:
                iterator = iter(names)

                item = next(iterator, null)

                if is_not_null(item):
                    iterator = prepend(item, iterator)

                if is_string(item):
                    original_names, names = names, []
                    values = []

                    for count, name in enumerate(original_names):
                        value = enum_type.enum_generate_next_value(
                            name, start, count, values.copy()
                        )

                        values.append(value)

                        names.append((name, value))

                    iterator = iter(names)

                namespace.update(iterator)

        namespace.update(members)

        # TODO: replace the frame hack if a blessed way to know the calling
        # module is ever developed
        if module is None:
            try:
                module = get_frame(DIRECT_CALLER if direct_call else NESTED_CALLER).f_globals[NAME]

            except (AttributeError, ValueError, KeyError):  # pragma: no cover
                pass

        if module is None:  # pragma: no cover
            make_namespace_unpicklable(namespace)

        else:
            namespace[MODULE] = module

        if qualified_name is None:
            if module is not None:
                qualified_name = QUALIFIED_NAME_STRING.format(module, flag_name)

        if qualified_name is not None:
            namespace[QUALIFIED_NAME] = qualified_name

        return meta.__new__(meta, flag_name, bases, namespace, boundary=boundary)

    def __repr__(self) -> str:
        """Returns the string used by [`repr`][repr] calls.

        By default contains the [`Flag`][enum_extensions.flags.Flag] name.

        Example:
            ```python
            >>> Permission
            <flag `Permission`>
            ```

        Returns:
            The string used in the [`repr`][repr] function.
        """
        return FLAG_REPRESENTATION.format(tick(get_name(self)))


    def _iter_member_by_value(self: Type[F], value: int) -> Iterator[F]:
        value_mapping = self._value_mapping

        for value in iter_bits(value & self._flag_mask):
            yield value_mapping[value]

    _iter_member = _iter_member_by_value

    def _iter_member_by_defintion(self: Type[F], value: int) -> Iterator[F]:
        return iter(
            sorted(
                self._iter_member_by_value(value),
                key=lambda flag: flag._sort_order,
            )
        )

    def _prepare_names(self, value: int) -> Tuple[List[str], int]:
        flag_mask = self._flag_mask

        unknown = value & ~flag_mask
        value &= flag_mask

        names = [flag.__enum_name__ for flag in self._iter_member(value)]

        return names, unknown

    def enum_missing(self: Type[F], value: int) -> F:
        """Handles *out-of-range* `value` according to given boundary.

        Arguments:
            value: The value to handle.

        Raises:
            ValueError: An invalid value was given.

        Returns:
            The matching flag member. See [`FlagBoundary`][enum_extensions.flags.FlagBoundary]
            for more information.
        """
        if not is_int(value):
            raise ValueError(INVALID_VALUE.format(repr(value), tick(get_name(self))))

        flag_mask = self._flag_mask
        all_bits = self._full_mask
        bit_length = self._bit_length

        boundary = self._boundary

        negative_value: Optional[int] = None

        if (
            # must be in range
            not ~all_bits <= value <= all_bits
            # must not include any skipped flags
            or value & (all_bits ^ flag_mask)
        ):
            if boundary is STRICT:
                bits = max(value.bit_length(), bit_length)

                raise ValueError(
                    INVALID_BITS.format(
                        hex(value), tick(get_name(self)), bin(value, bits), bin(flag_mask, bits)
                    )
                )

            elif boundary is CONFORM:
                value &= flag_mask

            elif boundary is KEEP:
                if value < 0:
                    negative_value = value
                    value = bit_at(max(bit_length, value.bit_length())) + value

            else:  # pragma: no cover
                raise ValueError(UNKNOWN_BOUNDARY.format(repr(boundary)))

        if value < 0:
            negative_value = value
            value += bit_at(bit_length)

        unknown = value & ~flag_mask

        if unknown and boundary is not KEEP:  # pragma: no cover  # TODO: cover?
            raise ValueError(UNKNOWN_VALUES.format(get_name(self), value, unknown, bin(unknown)))

        member = self.add_member(None, value)

        if negative_value is not None:
            self._value_mapping[negative_value] = member

        return member

    def add_member(self: Type[F], name: Optional[str], value: int) -> F:
        """Adds a new member to the [`Flag`][enum_extensions.flags.Flag].

        Example:
            ```python
            class Permission(Flag):
                R = 4
                W = 2
                X = 1

            permission = Permission.add_member("N", 0)  # <Perm.N: 0>
            ```

        Arguments:
            name: The name of a member.
            value: The value of a member.

        Raises:
            ValueError: The name is already used by another member.

        Returns:
            A newly created [`Flag`][enum_extensions.flags.Flag] member.
        """

        member = super().add_member(name, value)

        self._modify_mask_and_iter()

        return member

    def from_values(self: Type[F], *values: int, bound: bool = True) -> F:
        """Searches for flag members by values, combining them into a single composite member.

        Example:
            ```python
            >>> Permission.from_values(4, 2)
            <Permission.R|W: 6>
            ```

        Arguments:
            *values: The values to look up.
            bound: Whether to ignore invalid values.

        Raises:
            ValueError: An invalid value was encountered and `bound` is false.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """
        result = self(0)

        if bound:
            for value in values:
                result |= self.from_value(value)

        else:
            for value in values:
                result |= self.from_value(value, 0)

        return result

    def from_names(self: Type[F], *names: str) -> F:
        """Searches for flag members by names, combining them into a single composite member.

        Example:
            ```python
            >>> Permission.from_names("r", "w", "x")
            <Permission.R|W|X: 7>
            ```

        Arguments:
            *names: The names to look up.

        Raises:
            KeyError: An invalid name was encountered.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        result = self(0)

        for name in names:
            result |= self.from_name(name)

        return result

    def from_multiple_data(self: Type[F], *multiple_data: Union[int, str], bound: bool = True) -> F:
        """Searches for flag members by names or values, combining them into
        a single composite member.

        Example:
            ```python
            >>> Permission.from_multiple_data(0, "x")
            <Permission.X: 1>
            ```

        Arguments:
            *multiple_data: The names and values to look up.
            bound: Whether to ignore invalid entries.

        Raises:
            ValueError: Invalid data was encountered and `bound` is false.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        result = self(0)

        if bound:
            for data in multiple_data:
                result |= self.from_data(data)

        else:
            for data in multiple_data:
                result |= self.from_data(data, 0)

        return result


NOT_COVERED = "({} not covered)"
UNSUPPORTED_IN = "unsupported operand type(s) for `in`: {} and {}"

FLAG_MEMBER_REPRESENTATION = "<{}.{}: {}>"
FLAG_MEMBER_STRING = "{}.{}"


class Flag(Enum, metaclass=FlagType):
    """Support for bit flags."""

    __enum_value__: int

    def __iter__(self: FlagT) -> Iterator[FlagT]:
        """Returns an iterator over invididual (single-bit) flag members.

        Example:
            ```python
            >>> tuple(Permission.R | Permission.W)
            (<Permission.R: 4>, <Permission.W: 2>)
            ```

        Returns:
            An iterator over single-bit [`Flag`][enum_extensions.flags.Flag] members.
        """
        return type(self)._iter_member(self.__enum_value__)

    def __contains__(self: FlagT, flag: FlagT) -> bool:
        """Checks whether the `flag` is in [`Flag`][enum_extensions.flags.Flag].

        Example:
            ```python
            >>> rw = Permission.R | Permission.W
            >>> x = Permission.X
            >>> assert x not in rw
            ```

        Arguments:
            flag: The flag member to check.

        Raises:
            TypeError: `flag` is not an instance of [`Flag`][enum_extensions.flags.Flag].

        Returns:
            Whether the `flag` is contained in [`Flag`][enum_extensions.flags.Flag].
        """
        if not is_flag_member(flag):
            raise TypeError(
                UNSUPPORTED_IN.format(tick(get_name(type(flag))), tick(get_name(type(self))))
            )

        self_value = self.__enum_value__
        flag_value = flag.__enum_value__

        if not self_value or not flag_value:
            return False

        return is_same_type(flag, self) and flag_value & self_value == flag_value

    def __repr__(self) -> str:
        """Returns the string used by [`repr`][repr] calls.

        By default contains the [`Flag`][enum_extensions.flags.Flag] name along with the
        (composite) member name and value.

        Example:
            ```python
            >>> Permission.R | Permission.W | Permission.X
            <Permission.R|W|X: 7>
            ```

        Returns:
            The string used in the [`repr`][repr] function.
        """
        return FLAG_MEMBER_REPRESENTATION.format(
            get_name(type(self)), self.__enum_composite_name__, self.__enum_value__
        )

    def __str__(self) -> str:
        """Returns the string used by [`str`][str] calls.

        By default contains the [`Flag`][enum_extensions.flags.Flag] name along with the
        (composite) member name.

        Example:
            ```python
            >>> print(Permission.R | Permission.X)
            Permission.R|X
            ```

        Returns:
            The string used in the [`str`][str] function.
        """
        return FLAG_MEMBER_STRING.format(get_name(type(self)), self.__enum_composite_name__)

    def __len__(self) -> int:
        """Returns the number of bits in the member value.

        Example:
            ```python
            >>> len(Permission.N)
            0

            >>> len(Permission.R | Permission.W | Permission.X)
            3
            ```

        Returns:
            The bit count of the member value.
        """
        return bit_count(self.__enum_value__)

    def __bool__(self) -> bool:
        """Checks whether the value is non-zero.

        Returns:
            Whether the value is non-zero.
        """
        return bool(self.__enum_value__)

    def __or__(self: FlagT, other: FlagT) -> FlagT:
        """Combines values of flag members via the `|` (*OR*) operation.

        Example:
            ```python
            >>> Permission.R | Permission.X
            <Permission.R|X: 5>
            ```

        Arguments:
            other: The flag member to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """
        if is_same_type(other, self):
            return type(self)(self.__enum_value__ | other.__enum_value__)

        return NotImplemented

    def __and__(self: FlagT, other: FlagT) -> FlagT:
        """Combines values of flag members via the `&` (*AND*) operation.

        Example:
            ```python
            >>> Permission.X & (Permission.R | Permission.W)
            <Permission.N: 0>
            ```

        Arguments:
            other: The flag member to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        if is_same_type(other, self):
            return type(self)(self.__enum_value__ & other.__enum_value__)

        return NotImplemented

    def __xor__(self: FlagT, other: FlagT) -> FlagT:
        """Combines values of flag members via the `^` (*XOR*) operation.

        Example:
            ```python
            >>> (Permission.R | Permission.X) ^ (Permission.W | Permission.X)
            <Permission.R|W: 6>
            ```

        Arguments:
            other: The flag member to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        if is_same_type(other, self):
            return type(self)(self.__enum_value__ ^ other.__enum_value__)

        return NotImplemented

    def __invert__(self: FlagT) -> FlagT:
        """Inverts (`~`) the [`Flag`][enum_extensions.flags.Flag] member value.

        Example:
            ```python
            >>> ~Permission.N
            <Permission.R|W|X: 7>
            ```

        Returns:
            The inverted [`Flag`][enum_extensions.flags.Flag] member.
        """

        if self._boundary is KEEP:
            return type(self)(~self.__enum_value__)

        return type(self)(self.__enum_value__ ^ self._flag_mask)

    __ior__ = __or__
    __iand__ = __and__
    __ixor__ = __xor__

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__

    enum_generate_next_value = staticmethod(strict_bit_next_value)

    @dynamic_attribute
    def __enum_composite_name__(self) -> str:
        name = self.__enum_name__

        if name is None:
            value = self.__enum_value__

            if not value:
                return str(value)

            names, unknown = type(self)._prepare_names(value)

            if not names:
                return hex(unknown)

            if unknown:
                names.append(hex(unknown))

            return concat_pipe(names)

        return name

    @dynamic_attribute
    def __enum_composite_title_name__(self) -> str:
        name = self.__enum_name__

        if name is None:
            value = self.__enum_value__

            if not value:
                return str(value)

            names, unknown = type(self)._prepare_names(value)

            if not names:
                return hex(unknown)

            title = concat_comma_space(map(create_title, names))

            if unknown:
                return title + SPACE + NOT_COVERED.format(hex(unknown))

            return title

        return create_title(name)

    @dynamic_attribute
    def name(self) -> str:
        """The name of the [`Flag`][enum_extensions.flags.Flag] member."""

        return self.__enum_composite_name__

    @dynamic_attribute
    def title_name(self) -> str:
        """The human-readable name of the [`Flag`][enum_extensions.flags.Flag] member."""

        return self.__enum_composite_title_name__


def is_flag(item: AnyType) -> TypeGuard[Type[Flag]]:
    return is_subclass(item, Flag)


def is_flag_member(item: Any) -> TypeGuard[Flag]:
    return is_instance(item, Flag)


class IntFlag(int, Flag, boundary=KEEP):
    """Support for integer-like bit flags."""

    def __contains__(self: FlagT, other: Union[int, FlagT]) -> bool:
        """Checks whether `other` is in [`Flag`][enum_extensions.flags.Flag].

        Example:
            ```python
            IntPermission = IntFlag("IntPermission", R=4, W=2, X=1, N=0)

            r, w, x, n = IntPermission

            rx = r | x

            assert r in rx
            assert not w in rx
            assert x.value in rx
            ```

        Arguments:
            other: The flag member or value to check.

        Raises:
            TypeError: `other` is not an [`int`][int] or a
                [`Flag`][enum_extensions.flags.Flag] member.

        Returns:
            Whether `other` is contained in [`Flag`][enum_extensions.flags.Flag].
        """
        if is_int(other):
            other = type(self)(other)

        return super().__contains__(other)

    def __or__(self: FlagT, other: Union[int, FlagT]) -> FlagT:
        """Combines values (of flag members) via the `|` (*OR*) operation.

        Example:
            ```python
            >>> IntPermission.R | 2
            <IntPermission.R|W: 6>

            >>> IntPermission.W | IntPermission.X
            <IntPermission.W|X: 2>
            ```

        Arguments:
            other: The flag member or value to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """
        if is_int(other):
            other = type(self)(other)

        return super().__or__(other)

    def __and__(self: FlagT, other: Union[int, FlagT]) -> FlagT:
        """Combines values (of flag members) via the `&` (*AND*) operation.

        Example:
            ```python
            >>> IntPermission.W & (IntPermission.R | IntPermission.X)
            <IntPermission.N: 0>

            >>> IntPermission.X & 1
            <IntPermission.X: 1>
            ```

        Arguments:
            other: The flag member or value to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        if is_int(other):
            other = type(self)(other)

        return super().__and__(other)

    def __xor__(self: FlagT, other: Union[int, FlagT]) -> FlagT:
        """Combines values (of flag members) via the `^` (*XOR*) operation.

        Example:
            ```python
            >>> (IntPermission.W | IntPermission.X) ^ (IntPermission.R | IntPermission.X)
            <IntPermission.R|W: 6>

            >>> IntPermission.X ^ 1
            <IntPermission.N: 0>
            ```

        Arguments:
            other: The flag member or value to combine `self` with.

        Returns:
            The combined [`Flag`][enum_extensions.flags.Flag] member.
        """

        if is_int(other):
            other = type(self)(other)

        return super().__xor__(other)

    __ior__ = __or__
    __iand__ = __and__
    __ixor__ = __xor__

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__
