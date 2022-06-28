from builtins import isinstance as is_instance
from typing import Callable, Iterable, Optional, TypeVar
from typing import Type as TypingType

from mypy.nodes import TypeInfo
from mypy.plugin import AttributeContext, Plugin
from mypy.subtypes import is_equivalent
from mypy.typeops import make_simplified_union
from mypy.types import CallableType, Instance, LiteralType, ProperType, Type, get_proper_type

from typing_extensions import Final

T = TypeVar("T")
U = TypeVar("U")

Unary = Callable[[T], U]

ENUMS: Final = frozenset((
    "enum_extensions.enums.Enum",
    "enum_extensions.enums.IntEnum",
    "enum_extensions.enums.StringEnum",
))

FLAGS: Final = frozenset(("enum_extensions.flags.Flag", "enum_extensions.flags.IntFlag"))

ENUM_BASES: Final = ENUMS | FLAGS

NAME_ACCESS: Final = "{}.name"
DIRECT_NAME_ACCESS: Final = "{}.__enum_name__"

VALUE_ACCESS: Final = "{}.value"
DIRECT_VALUE_ACCESS: Final = "{}.__enum_value__"

ENUM_NAME_ACCESS = (
    frozenset(NAME_ACCESS.format(prefix) for prefix in ENUM_BASES)
    | frozenset(DIRECT_NAME_ACCESS.format(prefix) for prefix in ENUM_BASES)
)

ENUM_VALUE_ACCESS = (
    frozenset(VALUE_ACCESS.format(prefix) for prefix in ENUM_BASES)
    | frozenset(DIRECT_VALUE_ACCESS.format(prefix) for prefix in ENUM_BASES)
)

ENUM_REMOVED_PROPERTIES: Final = frozenset(("enum_start", "enum_ignore"))

ENUM_SPECIAL_PROPERTIES: Final = frozenset((
    "name", "value", "title_name", "__enum_name__", "__enum_value__", *ENUM_REMOVED_PROPERTIES
))

ENUM: Final = "enum_extensions.enums.Enum"

GENERATE_NEXT_VALUE: Final = "enum_generate_next_value"

AUTO: Final = "enum_extensions.auto.Auto"
INT: Final = "builtins.int"
STR: Final = "builtins.str"

NEW: Final = "__new__"

BUILTINS: Final = "builtins."


def enum_name_callback(context: AttributeContext) -> Type:
    enum_field_name = extract_underlying_field_name(context.type)

    if enum_field_name is None:
        return context.default_attr_type

    else:
        str_type = context.api.named_generic_type(STR, [])

        literal_type = LiteralType(enum_field_name, fallback=str_type)

        return str_type.copy_modified(last_known_value=literal_type)


def first(iterable: Iterable[T]) -> Optional[T]:
    for item in iterable:
        return item

    return None


def infer_value_type_with_auto_fallback(
    context: AttributeContext, proper_type: Optional[ProperType]
) -> Optional[Type]:
    if proper_type is None:
        return None

    if not (is_instance(proper_type, Instance) and proper_type.type.fullname == AUTO):
        return proper_type

    context_type = context.type

    assert is_instance(context_type, Instance)

    info = context_type.type

    generate_next_value = GENERATE_NEXT_VALUE

    type_with_generate_next_value = first(
        t for t in info.mro if t.names.get(generate_next_value)
    )

    if type_with_generate_next_value is None:
        return context.default_attr_type

    node = type_with_generate_next_value.names[GENERATE_NEXT_VALUE]

    node_type = get_proper_type(node.type)

    if is_instance(node_type, CallableType):
        if type_with_generate_next_value.fullname == ENUM:
            int_type = context.api.named_generic_type(INT, [])
            return int_type

        return get_proper_type(node_type.ret_type)

    return context.default_attr_type


def implements_new(info: TypeInfo) -> bool:
    new = NEW
    builtins = BUILTINS

    type_with_new = first(
        t for t in info.mro if t.names.get(new) and not t.fullname.startswith(builtins)
    )

    if type_with_new is None:
        return False

    return type_with_new.fullname not in ENUMS


def enum_value_callback(context: AttributeContext) -> Type:
    enum_field_name = extract_underlying_field_name(context.type)

    context_type = context.type

    if enum_field_name is None:
        if is_instance(context_type, Instance):
            info = context_type.type

            if implements_new(info):
                return context.default_attr_type

            nodes = (info.get(name) for name in info.names)

            node_types = (
                get_proper_type(node.type) if node else None
                for node in nodes
                if node is None or not node.implicit
            )

            proper_types = tuple(
                infer_value_type_with_auto_fallback(context, t)
                for t in node_types
                if t is None or not is_instance(t, CallableType)
            )

            underlying_type = first(proper_types)

            if underlying_type is None:
                return context.default_attr_type

            all_same_value_type = all(
                proper_type is not None and proper_type == underlying_type
                for proper_type in proper_types
            )

            if all_same_value_type:
                return underlying_type

            all_equivalent_types = all(
                proper_type is not None and is_equivalent(proper_type, underlying_type)
                for proper_type in proper_types
            )

            if all_equivalent_types:
                return make_simplified_union(proper_types)  # type: ignore

        return context.default_attr_type

    assert is_instance(context_type, Instance)

    info = context_type.type

    if implements_new(info):
        return context.default_attr_type

    node = info.get(enum_field_name)

    if node is None:
        return context.default_attr_type

    underlying_type = infer_value_type_with_auto_fallback(context, get_proper_type(node.type))

    if underlying_type is None:
        return context.default_attr_type

    return underlying_type


def extract_underlying_field_name(type: Type) -> Optional[str]:
    proper_type = get_proper_type(type)

    if not is_instance(proper_type, Instance):
        return None

    if not proper_type.type.is_enum:
        return None

    underlying_literal = proper_type.last_known_value

    if underlying_literal is None:
        return None

    return underlying_literal.value  # type: ignore


class EnumExtensionsPlugin(Plugin):
    def get_attribute_hook(self, fullname: str) -> Optional[Unary[AttributeContext, Type]]:
        if fullname in ENUM_NAME_ACCESS:
            return enum_name_callback

        if fullname in ENUM_VALUE_ACCESS:
            return enum_value_callback

        return None


def plugin(version: str) -> TypingType[EnumExtensionsPlugin]:
    return EnumExtensionsPlugin
