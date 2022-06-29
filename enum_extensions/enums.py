from __future__ import annotations

from builtins import getattr as get_attribute
from builtins import hasattr as has_attribute
from builtins import isinstance as is_instance
from builtins import issubclass as is_subclass
from builtins import setattr as set_attribute
from builtins import type as standard_type
from types import DynamicClassAttribute as dynamic_attribute
from types import MappingProxyType as MappingProxy
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Literal, TypeGuard, TypeVarTuple, Unpack

from enum_extensions.auto import MaybeAuto, is_auto
from enum_extensions.bits import is_single_bit
from enum_extensions.constants import (
    COMMA,
    DIRECT_CALLER,
    DOCUMENTATION,
    ENUM_DOCUMENTATION,
    ENUM_GENERATE_NEXT_VALUE,
    ENUM_IGNORE,
    ENUM_PRESERVE,
    ENUM_START,
    ENUM_VALUE,
    INVALID_NAMES,
    MEMBER_MAPPING_PRIVATE,
    MODULE,
    NAME,
    NESTED_CALLER,
    NEW,
    NEW_MEMBER,
    OBJECT_NEW,
    PICKLE_METHODS,
    QUALIFIED_NAME,
    REDUCE,
    SPACE,
    STRICT,
    UNKNOWN_PRIVATE,
    USELESS_NEW,
    UTF_8,
)
from enum_extensions.members import is_member, is_non_member
from enum_extensions.string import case_fold, case_fold_name, concat_comma_space, create_title, tick
from enum_extensions.types import Nullable, is_not_null, is_null, null
from enum_extensions.typing import (
    AnyType,
    DynamicCallable,
    DynamicTuple,
    EmptyTuple,
    MaybeIterable,
    Names,
    Namespace,
    Quaternary,
    StringDict,
    StringMapping,
    StringPairs,
    get_name,
    is_mapping,
    is_string,
    is_tuple,
)
from enum_extensions.utils import (
    get_frame,
    is_descriptor,
    is_double_under_name,
    make_namespace_unpicklable,
    prepend,
)

__all__ = (
    "EnumType",
    "Enum",
    "IntEnum",
    "StringEnum",
    "StrEnum",
    "is_enum",
    "is_enum_member",
    "enum_generate_next_value",
)

T = TypeVar("T", covariant=True)
E = TypeVar("E")

ET = TypeVar("ET")

EnumT = TypeVar("EnumT", bound="Enum")
EnumerationT = TypeVar("EnumerationT", bound="Type[Enum]")

ENUM_DEFINED = False

GenerateNextValue = Quaternary[str, Optional[T], int, Sequence[T], T]


def enum_generate_next_value(
    name: Optional[str], start: Optional[T], count: int, values: Sequence[T]
) -> T:
    """Generates an appropriate next value to use.

    Arguments:
        name: The name of the [`Enum`][enum_extensions.enums.Enum] member which needs a value.
        start: An initial value to use.
        count: The amount of already existing unique enumeration members.
        values: All previously defined members.

    Returns:
        The generated value.
    """
    raise NotImplementedError


ATTEMPT_TO_REUSE = "attempt to reuse name {}"
ALREADY_DEFINED = "name {} is already defined"
CAN_NOT_USE_AUTO = "can not use `auto` because `enum_generate_next_value` is not defined"


class EnumDict(Namespace):
    """Tracks enumeration members and ensures their names are not reused."""

    def __init__(self) -> None:
        self._generate_next_value: Optional[GenerateNextValue[Any]] = None
        self._start: Optional[Any] = None
        self._ignore: Set[str] = set()

        self._member_names: List[str] = []
        self._member_values: List[Any] = []

        self._mapping: StringDict[Any] = {}

        super().__init__()

    @property
    def generate_next_value(self) -> Optional[GenerateNextValue[Any]]:
        return self._generate_next_value

    @property
    def start(self) -> Optional[Any]:
        return self._start

    @property
    def ignore(self) -> Set[str]:
        return self._ignore

    def _set_generate_next_value(
        self, generate_next_value: Optional[GenerateNextValue[Any]]
    ) -> None:
        self._generate_next_value = generate_next_value

    def _set_start(self, start: Optional[Any]) -> None:
        self._start = start

    def _set_ignore(self, ignore: MaybeIterable[str]) -> None:
        if is_string(ignore):
            self._ignore = set(ignore.replace(COMMA, SPACE).strip().split())

        else:
            self._ignore = set(ignore)

    @property
    def member_names(self) -> List[str]:
        return self._member_names

    @property
    def member_values(self) -> List[Any]:
        return self._member_values

    @property
    def mapping(self) -> StringDict[Any]:
        return self._mapping

    def is_used(self, name: str) -> bool:
        return name in self

    def is_ignored(self, name: str) -> bool:
        return name in self.ignore

    def is_reserved(self, name: str) -> bool:
        return name in self.mapping

    def add_member(self, name: str, value: MaybeAuto[Any]) -> None:
        if is_auto(value):
            if is_null(value.value):
                generate_next_value = self.generate_next_value

                if generate_next_value is None:
                    raise RuntimeError(CAN_NOT_USE_AUTO)

                value.value = generate_next_value(
                    name, self.start, len(self.member_names), self.member_values.copy()
                )

            value = value.value

        self.mapping[name] = value

        self.member_names.append(name)
        self.member_values.append(value)

    def __setitem__(self, name: str, value: Any) -> None:
        if name == ENUM_GENERATE_NEXT_VALUE:
            self._set_generate_next_value(value)

        elif name == ENUM_IGNORE:
            self._set_ignore(value)

        elif name == ENUM_START:
            self._set_start(value)

        elif self.is_reserved(name):
            raise ValueError(ATTEMPT_TO_REUSE.format(tick(name)))

        elif is_member(value):
            value = value.value

            self.add_member(name, value)

        elif is_non_member(value):
            value = value.value

        elif self.is_ignored(name) or is_double_under_name(name) or is_descriptor(value):
            pass

        elif self.is_used(name):
            raise ValueError(ALREADY_DEFINED.format(tick(name)))

        else:
            self.add_member(name, value)

        super().__setitem__(name, value)

    def update(self, item: Union[StringMapping[Any], StringPairs[Any]], **items: Any) -> None:
        if is_mapping(item):
            for name, value in item.items():
                self[name] = value

        else:
            for name, value in item:
                self[name] = value

        for name, value in items.items():
            self[name] = value


Bases = TypeVarTuple("Bases")

EXCESSIVE = "excessive data types (using {}): {}"


class FindNew(Generic[T]):
    def __init__(self, function: DynamicCallable[T], save: bool, use_args: bool) -> None:
        self._function = function
        self._save = save
        self._use_args = use_args

    @property
    def function(self) -> DynamicCallable[T]:
        return self._function

    @property
    def save(self) -> bool:
        return self._save

    @property
    def use_args(self) -> bool:
        return self._use_args


def find_new(
    namespace: Namespace, data_type: Type[T], enum_type: Optional[EnumerationT]
) -> FindNew[T]:
    function = namespace.get(NEW)

    save = function is not None

    use_args = True

    if function is None:
        for name in (NEW_MEMBER, NEW):
            for type in (data_type, enum_type):
                target = get_attribute(type, name, None)

                if target not in USELESS_NEW:
                    function = target
                    break

            if function is not None:
                break

        else:
            function = OBJECT_NEW
            use_args = False

    return FindNew(function, save, use_args)


def traverse_data_types(bases: DynamicTuple[AnyType]) -> Iterator[AnyType]:
    for chain in bases:
        candidate: Optional[AnyType] = None

        for base in chain.__mro__:
            if base is object:  # not useful in our case
                continue

            elif is_enum(base):  # derived from enum -> try using its data type
                data_type = base._data_type

                if data_type is not object:  # something actually useful
                    yield data_type
                    break  # move onto the next chain

            elif NEW in vars(base):
                yield candidate or base  # if we have a candidate, yield it, and use base otherwise
                break

            else:
                candidate = base


def find_data_type(bases: DynamicTuple[AnyType]) -> AnyType:
    traverser = traverse_data_types(bases)

    data_type = next(traverser, object)

    excessive = list(traverser)

    if excessive:
        names = concat_comma_space(map(tick, map(get_name, excessive)))

        raise TypeError(EXCESSIVE.format(tick(data_type), names))

    return data_type


@overload
def find_enum_type(bases: EmptyTuple) -> None:
    ...


@overload
def find_enum_type(bases: Tuple[Unpack[Bases], EnumerationT]) -> EnumerationT:
    ...


def find_enum_type(bases: DynamicTuple[AnyType]) -> Optional[AnyType]:
    if not bases:
        return None

    *types, enum_type = bases

    if not is_enum(enum_type):
        raise TypeError  # TODO: message?

    if not enum_type.is_empty():
        raise TypeError  # TODO: message?

    return enum_type


def create_enum_member(
    name: Optional[str],
    value: Any,
    data_type: AnyType,
    enum_type: Type[EnumT],
    new_function: DynamicCallable[Any],
    new_use_args: bool,
    dynamic_attributes: Set[str],
    flag: bool = False,
) -> EnumT:
    # handle value and initialization

    if name is not None:
        if name in enum_type._member_mapping:
            raise ValueError(ATTEMPT_TO_REUSE.format(tick(name)))

    if is_tuple(value):  # do nothing if value is a tuple
        args = value

    else:  # wrap into a tuple otherwise
        args = (value,)

    if data_type is tuple:  # special case for tuple enums
        args = (args,)  # wrap another time

    if new_use_args:
        member = new_function(enum_type, *args)

        if not has_attribute(member, ENUM_VALUE):  # if the value was not defined already
            if data_type is not object:
                value = data_type(*args)

            member.__enum_value__ = value

    else:
        member = new_function(enum_type)

        if not has_attribute(member, ENUM_VALUE):  # if the value was not defined previously
            member.__enum_value__ = value

    enum_type._member_values.append(value)

    member.__enum_name__ = name
    member.__enum_type__ = enum_type
    member.__init__(*args)

    member._sort_order = len(member._member_names)  # for sorting by definition

    try:
        canonical_member = enum_type._value_mapping.get(value)

        if canonical_member is not None:
            if canonical_member.__enum_name__ is None:
                canonical_member.__enum_name__ = name

            member = canonical_member

        else:
            if name is not None:
                if flag:
                    if is_single_bit(value):
                        enum_type._member_names.append(name)

                else:
                    enum_type._member_names.append(name)

    except TypeError:  # not hashable
        for name, canonical_member in enum_type._member_mapping.items():
            if canonical_member.__enum_value__ == member.__enum_value__:
                if canonical_member.__enum_name__ is None:
                    canonical_member.__enum_name__ = name

                member = canonical_member

                break

        else:
            if name is not None:
                if flag:
                    if is_single_bit(value):
                        enum_type._member_names.append(name)

                else:
                    enum_type._member_names.append(name)

    if name is not None:
        # boost performance for any member that would not shadow dynamic attributes
        if name not in dynamic_attributes:
            set_attribute(enum_type, name, member)

        # now add to member mapping
        enum_type._member_mapping[name] = member

    try:
        # attempt to add to value -> member map in order to make lookups constant, O(1)
        # if value is not hashable, this will fail and our lookups will be linear, O(n)
        enum_type._value_mapping.setdefault(value, member)  # in order to support threading

    except TypeError:
        pass

    return member  # return newly created member in case someone needs to use it


INVALID_MEMBER_NAMES = "invalid member names: {}"
CAN_NOT_DELETE_MEMBER = "can not delete enum member: {}"
CAN_NOT_REASSIGN_MEMBER = "can not reassign enum member: {}"

ENUM_REPRESENTATION = "<enum {}>"
QUALIFIED_NAME_STRING = "{}.{}"

UNKNOWN = "UNKNOWN"


class EnumType(type):
    """Metaclass for [`Enum`][enum_extensions.enums.Enum].

    [`EnumType`][enum_extensions.enums.EnumType] is responsible for setting
    the correct methods on the final *enumeration*, as well as creating the *members*,
    properly handling duplicates, providing iteration over the enumeration members, etc.
    """

    _unknown: bool
    _flag: bool
    _start: Optional[Any]
    _member_names: List[str]
    _member_values: List[Any]
    _data_type: AnyType
    _new_function: DynamicCallable[Any]
    _new_use_args: bool
    _member_mapping: StringDict[Enum]
    _value_mapping: Dict[Any, Enum]
    _dynamic_attributes: Set[str]

    @classmethod
    def __prepare__(
        cls,
        name: str,
        bases: DynamicTuple[AnyType],
        *,
        ignore: Optional[MaybeIterable[str]] = None,
        start: Optional[Any] = None,
        unknown: Optional[bool] = None,
        flag: bool = False,
        **kwargs: Any,
    ) -> EnumDict:
        namespace = EnumDict()

        enum_type = find_enum_type(bases)

        namespace[ENUM_GENERATE_NEXT_VALUE] = get_attribute(
            enum_type, ENUM_GENERATE_NEXT_VALUE, None
        )

        if ignore is not None:
            namespace[ENUM_IGNORE] = ignore

        namespace[ENUM_START] = start

        return namespace

    def __new__(
        cls: Type[ET],
        enum_name: str,
        bases: DynamicTuple[AnyType],
        namespace: EnumDict,
        *,
        ignore: Optional[MaybeIterable[str]] = None,
        start: Optional[Any] = None,
        unknown: Optional[bool] = None,
        flag: bool = False,
        **kwargs: Any,
    ) -> ET:
        global ENUM_DEFINED

        # add `enum_ignore` to itself
        enum_ignore = namespace.ignore
        enum_ignore.add(ENUM_IGNORE)

        # remove all names in `enum_ignore`
        for name in enum_ignore:
            if name in namespace:
                del namespace[name]

        enum_type = find_enum_type(bases)  # type: ignore

        if enum_type is None and ENUM_DEFINED:
            enum_type = Enum

        data_type = find_data_type(bases)

        new = find_new(namespace, data_type, enum_type)

        enum_members = namespace.mapping.copy()

        # remove enum members so they do not get into new enum type
        for name in namespace.member_names:
            if name in namespace:
                del namespace[name]

        # check for invalid names
        invalid_names = set(enum_members) & INVALID_NAMES

        if invalid_names:
            names = concat_comma_space(map(tick, invalid_names))

            raise ValueError(INVALID_MEMBER_NAMES.format(names))

        namespace.setdefault(DOCUMENTATION, ENUM_DOCUMENTATION)

        # handle reduce
        if REDUCE not in namespace:
            if data_type is not object:
                pickle_methods = set(vars(data_type)) & PICKLE_METHODS

                if not pickle_methods:
                    make_namespace_unpicklable(namespace)

        # create dummy enum type

        dummy_enum_type = super().__new__(cls, enum_name, bases, EnumDict())

        # manipulate Method Resolution Order (MRO)

        mro = list(dummy_enum_type.mro())

        try:
            mro.remove(dummy_enum_type)

        except ValueError:  # pragma: no cover
            pass

        try:
            if mro.index(data_type) < mro.index(enum_type):
                # we need to preserve enum_type functions
                mro.remove(enum_type)
                mro.insert(mro.index(data_type), enum_type)

        except ValueError:  # pragma: no cover
            pass

        bases = tuple(mro)  # now back to tuple

        # create new enum type
        new_enum_type = super().__new__(cls, enum_name, bases, namespace)

        # on top of it, preserve names that should ideally belong to enums
        for name in ENUM_PRESERVE:
            if name in namespace:
                continue

            type_method = get_attribute(new_enum_type, name)
            data_method = get_attribute(data_type, name, None)
            enum_method = get_attribute(enum_type, name, None)

            if data_method is not None and data_method is type_method:
                set_attribute(new_enum_type, name, enum_method)

        if unknown is None:
            unknown = get_attribute(new_enum_type, UNKNOWN_PRIVATE, False)

        # add information
        new_enum_type._flag = flag
        new_enum_type._unknown = unknown
        new_enum_type._start = namespace.start
        new_enum_type._member_names = []
        new_enum_type._member_values = []
        new_enum_type._data_type = data_type
        new_enum_type._new_function = new.function
        new_enum_type._new_use_args = new.use_args

        # add mappings
        new_enum_type._member_mapping = {}  # name -> member
        new_enum_type._value_mapping = {}  # value -> member (if hashable)

        # save dynamic attributes to know if we an take the shortcut of
        # storing members in the type dict
        dynamic_attributes = {
            name
            for type in new_enum_type.mro()
            for name, value in vars(type).items()
            if is_instance(value, dynamic_attribute)
        }

        new_enum_type._dynamic_attributes = dynamic_attributes

        # create fellow enum members
        for name, value in enum_members.items():
            create_enum_member(
                name,
                value,
                data_type,
                new_enum_type,
                new.function,
                new.use_args,
                dynamic_attributes,
                flag,
            )

        # save new if needed
        if ENUM_DEFINED:
            if new.save:
                new_enum_type.__new_member__ = new.function

            new_enum_type.__new__ = Enum.__new__

        else:
            ENUM_DEFINED = True

        return new_enum_type

    @overload
    def __call__(self: Type[E], value: Any) -> E:
        ...

    @overload
    def __call__(
        self: ET,
        value: str,
        names: Optional[Names] = ...,
        *,
        module: Optional[str] = ...,
        qualified_name: Optional[str] = ...,
        type: Optional[AnyType] = ...,
        start: Optional[Any] = ...,
        unknown: Optional[bool] = ...,
        **members: Any,
    ) -> ET:
        ...

    def __call__(
        self: Type[E],
        value: Any,
        names: Optional[Names] = None,
        *,
        module: Optional[str] = None,
        qualified_name: Optional[str] = None,
        type: Optional[AnyType] = None,
        start: Optional[Any] = None,
        unknown: Optional[bool] = None,
        **members: Any,
    ) -> Union[E, Type[E]]:
        """Looks up an existing member or creates a new enumeration.

        Example:
            Creation:

            ```python
            Color = Enum("Color", RED=1, GREEN=2, BLUE=3)
            ```

            Value lookup:

            ```python
            green = Color(2)  # <Color.GREEN: 2>
            ```

        Arguments:
            value: The value to search for or the name of the
                new [`Enum`][enum_extensions.enums.Enum] to create.
            names: The names/values of the new enumeration members.
            module: The name of the module the [`Enum`][enum_extensions.enums.Enum] is created in.
            qualified_name: The actual location in the module where the enumeration can be found.
            type: A data type of the new [`Enum`][enum_extensions.enums.Enum].
            start: The initial value of the new enumeration
                (used by [`auto`][enum_extensions.auto.auto]).
            unknown: Whether to enable unknown values of enumeration members.
                [`None`][None] means that it should be inherited.
                The default value in the end is [`False`][False].
            **members: A `name -> value` mapping of [`Enum`][enum_extensions.enums.Enum] members.

        Raises:
            ValueError: The member was not found.

        Returns:
            A newly created [`Enum`][enum_extensions.enums.Enum] type or a member found.
        """
        if names or module or qualified_name or type or start or unknown or members:
            return self.create(
                value,
                names,
                module=module,
                qualified_name=qualified_name,
                type=type,
                start=start,
                unknown=unknown,
                direct_call=False,
                **members,
            )

        return self.__new__(self, value)

    def create(
        self: ET,
        enum_name: str,
        names: Optional[Names] = None,
        *,
        module: Optional[str] = None,
        qualified_name: Optional[str] = None,
        type: Optional[AnyType] = None,
        start: Optional[Any] = None,
        unknown: Optional[bool] = None,
        direct_call: bool = True,
        **members: Any,
    ) -> ET:
        """Creates a new enumeration.

        Example:
            ```python
            Color = Enum("Color", ("RED", "GREEN", "BLUE"))
            ```

        Arguments:
            enum_name: The name of the new [`Enum`][enum_extensions.enums.Enum] to create.
            names: The names/values of the new enumeration members.
            module: The name of the module the [`Enum`][enum_extensions.enums.Enum] is created in.
            qualified_name: The actual location in the module where the enumeration can be found.
            type: A data type of the new [`Enum`][enum_extensions.enums.Enum].
            start: The initial value of the new enumeration
                (used by [`auto`][enum_extensions.auto.auto]).
            unknown: Whether to enable unknown values of enumeration members.
                [`None`][None] means that it should be deduced from inheritance.
                The default value in the end is [`False`][False].
            direct_call: Controls if the function is called directly or not.
                Use this argument with caution.
            **members: A `name -> value` mapping of [`Enum`][enum_extensions.enums.Enum] members.

        Returns:
            A newly created [`Enum`][enum_extensions.enums.Enum] type.
        """

        meta = standard_type(self)

        bases = (self,) if type is None else (type, self)

        enum_type = find_enum_type(bases)

        namespace = meta.__prepare__(enum_name, bases, start=start, unknown=unknown)

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

            except (AttributeError, ValueError, KeyError):
                pass

        if module is None:
            make_namespace_unpicklable(namespace)

        else:
            namespace[MODULE] = module

        if qualified_name is None:
            if module is not None:
                qualified_name = QUALIFIED_NAME_STRING.format(module, enum_name)

        if qualified_name is not None:
            namespace[QUALIFIED_NAME] = qualified_name

        return meta.__new__(meta, enum_name, bases, namespace, unknown=unknown)

    def is_empty(self) -> bool:
        """Checks whether the enumeration does not contain any members.

        Example:
            ```python
            class Test(Enum):
                TEST = 42

            assert Enum.is_empty()
            assert not Test.is_empty()
            ```
        """
        return not self._member_values

    def add_member(self: Type[E], name: Optional[str], value: Any) -> E:
        """Adds a new member to the enumeration.

        Example:
            ```python
            class Color(Enum):
                RED = 1
                GREEN = 2
                BLUE = 3

            black = Color.add_member("BLACK", 0)  # <Color.BLACK: 0>
            ```

        Arguments:
            name: The name of a member.
            value: The value of a member.

        Raises:
            ValueError: The name is already used by another member.

        Returns:
            A newly created [`Enum`][enum_extensions.enums.Enum] member.
        """
        if is_auto(value):
            if is_null(value.value):
                value.value = self.enum_generate_next_value(
                    name, self._start, len(self._member_names), self._member_values.copy()
                )

            value = value.value

        return create_enum_member(
            name,
            value,
            self._data_type,
            self,
            self._new_function,
            self._new_use_args,
            self._dynamic_attributes,
            self._flag,
        )

    def update(self: Type[E], **name_to_value: Any) -> None:
        """Updates the enumeration, adding members to it.

        Example:
            ```python
            class Color(Enum):
                RED = 1
                GREEN = 2
                BLUE = 3

            Color.update(BLACK=0, WHITE=4)

            colors = (Color.BLACK, Color.WHITE)  # (<Color.BLACK: 0>, <Color.WHITE: 4>)
            ```

        Arguments:
            **name_to_value: Keywords argument in `name -> value` form.

        Raises:
            ValueError: The name in `name_to_value` is already used by another member.
        """
        for name, value in name_to_value.items():
            self.add_member(name, value)

    def __bool__(self) -> Literal[True]:
        return True

    def __contains__(self: Type[E], data: Any) -> bool:
        """Checks whether the `data` is in [`Enum`][enum_extensions.enums.Enum].

        `data` is contained in enumeration if:

        - `data` is a member of said enumeration, or
        - `data` is the value of one of the members.

        Example:
            ```python
            class Color(Enum):
                RED = 1
                GREEN = 2
                BLUE = 3

            assert Color.RED in Color
            assert 3 in Color
            assert 0 not in Color
            ```

        Arguments:
            data: The data to check.

        Returns:
            Whether the `data` is contained in [`Enum`][enum_extensions.enums.Enum].
        """
        if is_instance(data, self):
            return True

        try:
            return data in self._value_mapping

        except TypeError:
            return data in self._member_values

    def __delattr__(self, name: str) -> None:
        if name in self._member_mapping:
            raise AttributeError(CAN_NOT_DELETE_MEMBER.format(tick(name)))

        super().__delattr__(name)

    def __getattr__(self: Type[E], name: str) -> E:
        """Returns the [`Enum`][enum_extensions.enums.Enum] member matching `name`.

        Example:
            ```python
            >>> Color.BLUE
            <Color.BLUE: 3>
            ```

        Arguments:
            name: The name of the member to find.

        Raises:
            AttributeError: The member was not found.

        Returns:
            The member found.
        """
        if is_double_under_name(name):
            raise AttributeError(name)

        try:
            return self._member_mapping[name]

        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(self: Type[E], name: str) -> E:
        """Returns the [`Enum`][enum_extensions.enums.Enum] member matching `name`.

        Example:
            ```python
            >>> Color["GREEN"]
            <Color.GREEN: 2>
            ```

        Arguments:
            name: The name of the member to find.

        Raises:
            KeyError: The member was not found.

        Returns:
            The member found.
        """
        return self._member_mapping[name]

    def __iter__(self: Type[E]) -> Iterator[E]:
        """Returns an iterator over unique [`Enum`][enum_extensions.enums.Enum] members in
        definition order.

        Example:
            ```python
            >>> tuple(Color)
            (<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>)
            ```

        Returns:
            An iterator of unique [`Enum`][enum_extensions.enums.Enum] members.
        """
        return self.iter_members()

    def __reversed__(self: Type[E]) -> Iterator[E]:
        """Returns an iterator over unique [`Enum`][enum_extensions.enums.Enum] members in
        reverse definition order.

        Example:
            ```python
            >>> tuple(reversed(Color))
            (<Color.BLUE: 3>, <Color.GREEN: 2>, <Color.RED: 1>)
            ```

        Returns:
            An iterator of unique [`Enum`][enum_extensions.enums.Enum] members.
        """
        return self.iter_members(reverse=True)

    def __len__(self) -> int:
        """Returns the number of unique members (excluding aliases).

        Example:
            ```python
            >>> len(Color)
            3
            ```

        Returns:
            The count of unique enumeration members.
        """
        return len(self._member_names)

    def __repr__(self) -> str:
        """Returns the string used by [`repr`][repr] calls.

        By default contains the [`Enum`][enum_extensions.enums.Enum] name.

        Example:
            ```python
            >>> Color
            <enum `Color`>
            ```

        Returns:
            The string used in the [`repr`][repr] function.
        """
        return ENUM_REPRESENTATION.format(tick(get_name(self)))

    def __setattr__(self, name: str, value: Any) -> None:
        member_mapping = vars(self).get(MEMBER_MAPPING_PRIVATE, {})  # prevent recursion

        if name in member_mapping:
            raise AttributeError(CAN_NOT_REASSIGN_MEMBER.format(tick(name)))

        super().__setattr__(name, value)

    def iter_members(self: Type[E], reverse: bool = False) -> Iterator[E]:
        """Returns an iterator over unique enumeration members in definition order,
        optionally reversing it.

        Example:
            ```python
            >>> list(Color.iter_members())
            [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]
            >>> list(Color.iter_members(reverse=True))
            [<Color.BLUE: 3>, <Color.GREEN: 2>, <Color.RED: 1>]
            ```

        Arguments:
            reverse: Whether to reverse the definition order.

        Returns:
            An iterator over unique members.
        """
        names = self._member_names

        if reverse:
            names = reversed(names)

        member_mapping = self._member_mapping

        return (member_mapping[name] for name in names)

    @property
    def members(self: Type[E]) -> StringMapping[E]:
        """An immutable mapping of enumeration members (including aliases).

        Example:
            ```python
            >>> for name, member in self.members.items():
            ...     print(name, member)

            RED Color.RED
            GREEN Color.GREEN
            BLUE Color.BLUE
            ```

        Returns:
            An immutable mapping of all enumeration members.
        """
        return MappingProxy(self._member_mapping)

    __members__ = members

    @property
    def case_fold_names(self: Type[E]) -> StringMapping[E]:
        return {case_fold_name(name): member for name, member in self._member_mapping.items()}

    def from_name(self: Type[E], name: str) -> E:
        """Finds a member by name case insensitively.

        Example:
            ```python
            class Test(Enum):
                TEST = 13

            test = Test.from_name("test")  # <Test.TEST: 13>
            ```

        Arguments:
            name: The CI (case insensetive) name to look up.

        Raises:
            KeyError: Member is not found.

        Returns:
            The [`Enum`][enum_extensions.enums.Enum] member found.
        """
        return self.case_fold_names[case_fold_name(name)]

    def from_value(self: Type[E], value: Any, default: Nullable[Any] = null) -> E:
        """Finds a member by value with an optional `default` value fallback.

        Example:
            ```python
            class Test(Enum):
                TEST = 25

            test = Test.from_value(25)  # <Test.TEST: 25>
            ```

        Arguments:
            value: The value to look up.
            default: The default value to fall back to.

        Raises:
            ValueError: Member is not found and `default` is not provided.

        Returns:
            The [`Enum`][enum_extensions.enums.Enum] member found.
        """
        try:
            return self(value)

        except ValueError:
            if is_null(default):
                raise

            return self(default)

    def from_data(self: Type[E], data: Any, default: Nullable[Any] = null) -> E:
        """Finds a member by name or by value with an optional `default` value fallback.

        Example:
            ```python
            class Test(Enum):
                TEST = 42

            test = Test.from_data("test")  # <Test.TEST: 42>
            test = Test.from_data(42)  # <Test.TEST: 42>
            ```

        Arguments:
            data: The name or value to look up.
            default: The default value to fall back to.

        Raises:
            ValueError: Member is not found and `default` is not provided.

        Returns:
            The [`Enum`][enum_extensions.enums.Enum] member found.
        """
        if is_string(data):
            try:
                return self.from_name(data)

            except KeyError:
                pass

        return self.from_value(data, default)

    def enum_missing(self: Type[E], value: Any) -> Optional[E]:
        if self._unknown:
            return self.add_member(None, value)

        return None


INVALID_VALUE = "{} is not a valid {}"
ENUM_MISSING_ERROR = "error in `{}.enum_missing`: returned {} instead of None or a member"

ENUM_MEMBER_REPRESENTATION = "<{}.{}: {}>"
ENUM_MEMBER_STRING = "{}.{}"


def incremental_next_value(
    name: str, start: Optional[Any], count: int, values: Sequence[Any]
) -> Any:
    if start is None:
        start = 1

    for value in reversed(values):
        try:
            return value + 1

        except TypeError:
            pass

    return start


class Enum(metaclass=EnumType):
    """A collection of `name -> value` pairs.

    Example enumeration:

    ```python
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3
    ```

    Accessing members via attributes:

    ```python
    >>> Color.RED
    <Color.RED: 1>
    ```

    Getting members by name:

    ```python
    >>> Color["GREEN"]
    <Color.GREEN: 2>
    ```

    Alternatively, using values:

    ```python
    >>> Color(3)
    <Color.BLUE: 3>
    ```

    Enumerations can be iterated over, and know how many members they have:

    ```python
    >>> len(Color)
    3
    >>> list(Color)
    [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]
    ```

    Methods can be added to enumerations, and members can have their own
    attributes; see the documentation for details.
    """

    __enum_name__: Optional[str]
    __enum_value__: Any

    _sort_order: int

    def __new__(cls: Type[EnumT], value: Any) -> EnumT:
        """Looks up the member by value.

        Example:
            ```python
            >>> Color(1)
            <Color.RED: 1>
            ```

        Arguments:
            value: The value to search for.

        Raises:
            ValueError: The member was not found.

        Returns:
            The [`Enum`][enum_extensions.enums.Enum] member found.
        """
        # all enum members are created during type construction without calling this method

        if type(value) is cls:
            return value

        try:
            return cls._value_mapping[value]

        except KeyError:
            # not found, no need to do O(n) search
            pass

        except TypeError:
            # not hashable, then do long search, O(n) behavior
            for member in cls._member_mapping.values():
                if member.__enum_value__ == value:
                    return member

        error = None

        # still not found -> try enum_missing hook
        try:
            result = cls.enum_missing(value)  # type: ignore

        except AttributeError:
            result = None

        except Exception as error_happened:
            error = error_happened
            result = None

        if is_instance(result, cls):
            return result

        else:
            error_invalid = ValueError(INVALID_VALUE.format(repr(value), tick(get_name(cls))))

            if result is None and error is None:  # no result, no error
                raise error_invalid

            if error is None:
                error = ValueError(ENUM_MISSING_ERROR.format(get_name(cls), repr(result)))

            raise error_invalid from error

    def __repr__(self) -> str:
        """Returns the string used by [`repr`][repr] calls.

        By default contains the [`Enum`][enum_extensions.enums.Enum] name
        along with member name and value.

        Example:
            ```python
            >>> Color.BLUE
            <Color.BLUE: 3>
            ```

        Returns:
            The string used in the [`repr`][repr] function.
        """
        return ENUM_MEMBER_REPRESENTATION.format(
            get_name(type(self)), self.__enum_checked_name__, self.__enum_value__
        )

    def __str__(self) -> str:
        """Returns the string used by [`str`][str] calls.

        By default contains the [`Enum`][enum_extensions.enums.Enum] name along with member name.

        Example:
            ```python
            >>> print(Color.BLUE)
            Color.BLUE
            ```

        Returns:
            The string used in the [`str`][str] function.
        """
        return ENUM_MEMBER_STRING.format(get_name(type(self)), self.__enum_checked_name__)

    def __format__(self, specification: str) -> str:
        """Returns the string used by [`format`][format] calls and f-strings.

        By default this function gives the same result as [`str`][str] does.

        Example:
            ```python
            >>> color = Color.RED
            >>> print(f"{color}")
            Color.RED
            ```

        Returns:
            The string used in the [`format`][format] function and f-strings.
        """
        data_type = self._data_type

        if data_type is object:
            type, value = str, str(self)

        else:
            type, value = data_type, self.__enum_value__

        return type.__format__(value, specification)

    def __hash__(self) -> int:
        return hash(self.__enum_name__)

    def __reduce_ex__(self: EnumT, protocol: Any) -> Tuple[Type[EnumT], Tuple[Any]]:
        return type(self), (self.__enum_value__,)

    @dynamic_attribute
    def __enum_checked_name__(self) -> str:
        name = self.__enum_name__

        return UNKNOWN if name is None else name

    @dynamic_attribute
    def name(self) -> str:
        """The name of the [`Enum`][enum_extensions.enums.Enum] member."""
        return self.__enum_checked_name__

    @dynamic_attribute
    def value(self) -> Any:
        """The value of the [`Enum`][enum_extensions.enums.Enum] member."""
        return self.__enum_value__

    @dynamic_attribute
    def title_name(self) -> str:
        """The human-readable name of the [`Enum`][enum_extensions.enums.Enum] member."""
        return create_title(self.__enum_checked_name__)

    enum_generate_next_value = staticmethod(incremental_next_value)


USELESS_NEW.add(Enum.__new__)


def is_enum(item: AnyType) -> TypeGuard[Type[Enum]]:
    return is_subclass(item, Enum)


def is_enum_member(item: Any) -> TypeGuard[Enum]:
    return is_instance(item, Enum)


def case_fold_name_next_value(
    name: str, start: Optional[str], count: int, values: Sequence[str]
) -> str:
    return case_fold(name)


class IntEnum(int, Enum):
    """An enumeration whose values are (and must be) integers."""


buffer = Union[bytes, bytearray, memoryview]

S = TypeVar("S", bound="StringEnum")


class StringEnum(str, Enum):
    """An enumeration whose values are (and must be) strings."""

    @overload
    def __new__(cls: Type[S], item: buffer, encoding: str = ..., errors: str = ...) -> S:
        ...

    @overload
    def __new__(cls: Type[S], item: Any) -> S:
        ...

    def __new__(cls: Type[S], item: Any, encoding: str = UTF_8, errors: str = STRICT) -> S:
        if is_string(item):
            value = item

        else:
            value = str(item, encoding, errors)

        member = str.__new__(cls, value)

        member.__enum_value__ = value

        return member

    enum_generate_next_value = staticmethod(case_fold_name_next_value)


StrEnum = StringEnum
