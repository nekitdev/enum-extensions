# Enums

## Prerequisites

Code snippets and examples below are using several common imports and types,
which are mainly omitted for simplicity:

```python
from typing import TypeVar  # for various typing purposes

from enum_extensions import (  # library imports used in examples
    # enumerations
    Enum,
    IntEnum,
    StringEnum,
    # auto items
    auto,
    # (non-)members
    member,
    non_member,
)

T = TypeVar("T")  # general (and generic) type variable

E = TypeVar("E", bound=Enum)  # enum type variable
```

## Creating Enumerations

There are many ways to create enumerations.

This can be done in a classical way:

```python
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

Similar to the standard [`enum`][enum] module, `enum-extensions`
has an [`Auto`][enum_extensions.auto.Auto] type and
an [`auto`][enum_extensions.auto.auto] function:

```python
class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
```

Enumerations can be created without explicit `class` usage:

```python
Color = Enum("Color", ("RED", "GREEN", "BLUE"))
```

Strings can also be used here:

```python
Color = Enum("Color", "RED GREEN BLUE")
```

Mappings work just as nicely:

```python
Color = Enum("Color", {"RED": 1, "GREEN": 2, "BLUE": 3})
```

You can also use keyword arguments in order to define members:

```python
Color = Enum("Color", RED=1, GREEN=2, BLUE=3)
```

Same with [`auto`][enum_extensions.auto.auto], of course:

```python
Color = Enum("Color", RED=auto(), GREEN=auto(), BLUE=auto())
```

All code snippets above produce `Color` enumeration in the end, which has the following members:

- `<Color.RED: 1>`
- `<Color.GREEN: 2>`
- `<Color.BLUE: 3>`

See [`Enum.create`][enum_extensions.enums.EnumType.create] documentation
for more details on creation API.

## Member Attributes

Enumeration members have several useful attributes:

- [`name`][enum_extensions.enums.Enum.name], which represents their actual name;
- [`value`][enum_extensions.enums.Enum.value], which contains their value;
- [`title_name`][enum_extensions.enums.Enum.title_name], which is a more
  human-readable version of their [`name`][enum_extensions.enums.Enum.name].

## Member Access

Consider the following enumeration:

```python
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

Enumeration members can be accessed by their name via attributes:

```python
red = Color.RED  # <Color.RED: 1>
```

Or via subscription:

```python
green = Color["GREEN"]  # <Color.GREEN: 2>
```

Alternatively, by-value access can be used:

```python
blue = Color(3)  # <Color.BLUE: 3>
```

## Advanced Access

Enumeration members can be accessed with case insensitive strings
(via [`Enum.from_name`][enum_extensions.enums.EnumType.from_name]):

```python
class Test(Enum):
    TEST = 13

test = Test.from_name("test")  # <Test.TEST: 13>
```

**Note that if two members have same case insensitive name version, last in wins!**

*Also keep in mind [`Enum.from_name`][enum_extensions.enums.EnumType.from_name]*
*will not work with composite flags!*

Non-existent names raise a [`KeyError`][KeyError]:

```python
>>> Test.from_name("unknown")

Traceback (most recent call last):
  ...
KeyError: "unknown"
```

There is also [`Enum.from_value`][enum_extensions.enums.EnumType.from_value],
which can be used to lookup members by value, optionally defaulting to some value:

```python
class Test(Enum):
    TEST = 25

test = Test.from_value(25)  # <Test.TEST: 25>
default = Test.from_value(42, 25)  # <Test.TEST: 25>
```

Non-present values without fallback will to raise a [`ValueError`][ValueError]:

```python
>>> Test.from_value(42)

Traceback (most recent call last):
  ...
ValueError: 42 is not a valid `Test`
```

[`Enum.from_data`][enum_extensions.enums.EnumType.from_data] is used to
find members either by name or by value with an optional default.
[`Enum.from_name`][enum_extensions.enums.EnumType.from_name] is called if given a string,
and otherwise (including on failure),
[`Enum.from_value`][enum_extensions.enums.EnumType.from_value] is applied with `default`:

```python
class Test(Enum):
    TEST = 42

test = Test.from_data("test")  # <Test.TEST: 42>
test = Test.from_data(42)  # <Test.TEST: 42>
test = Test.from_data(25, 42)  # <Test.TEST: 42>
```

Unknown names or values raise a [`ValueError`][ValueError]:

```python
>>> Test.from_data(13)

Traceback (most recent call last):
  ...
ValueError: 13 is not a valid `Test`

>>> Test.from_data("unknown")

Traceback (most recent call last):
  ...
ValueError: "unknown" is not a valid `Test`
```

## Iteration

It is possible to iterate over unique enumeration members:

```python
>>> Color = Enum("Color", RED=1, GREEN=2, BLUE=3)

>>> for color in Color:
...     print(Color.title)

Red
Green
Blue
```

Or over all members, including aliases:

```python
>>> Color = Enum("Color", RED=1, GREEN=2, BLUE=3, R=1, G=2, B=3)

>>> for name, color in Color.members.items():
...     print(name, color.name)

RED RED
GREEN GREEN
BLUE BLUE
R RED
G GREEN
B BLUE
```

## Length

Enumerations are aware of their unique member count, which can be accessed using [`len`][len]:

```python
>>> Color = Enum("Color", ("RED", "GREEN", "BLUE"))
>>> len(Color)
3
```

## Container Checks

Enumerations can check if the member belongs to them:

```python
>>> Color = Enum("Color", RED=1, GREEN=2, BLUE=3)
>>> Shade = Enum("Shade", BLACK=0, WHITE=100)
>>> Color.BLUE in Color
True
>>> Shade.WHITE in Shade
True
>>> Color.GREEN in Shade
False
>>> Shade.BLACK in Color
False
```

This also works nicely with values:

```python
>>> 1 in Color
True
>>> 100 in Color
False
```

## Initialization Arguments

Enumeration members that have [`tuple`][tuple] values but do not subclass [`tuple`][tuple]
are interpreted as values passed to [`__init__`][object.__init__] of their class:

```python
from math import sqrt

class Point:
    ORIGIN = (0, 0)

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    @property
    def distance_from_origin(self) -> float:
        return sqrt(self.x * self.x + self.y * self.y)

origin = Point.ORIGIN  # <Point.ORIGIN: (0, 0)>

print(origin.value)  # (0, 0)
print(origin.distance_from_origin)  # 0.0
```

## Mutability

Taking the (extremely familiar) enumeration:

```python
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

Members can not be deleted:

```python
>>> del Color.RED

Traceback (most recent call last):
  ...
AttributeError: can not delete enum member: `RED`
```

They can not be reassigned, either:

```python
>>> Color.BLUE = 0

Traceback (most recent call last):
  ...
AttributeError: can not reassign enum member: `BLUE`
```

However, new members can be added to an enumeration via
[`Enum.add_member`][enum_extensions.enums.EnumType.add_member] or
[`Enum.update`][enum_extensions.enums.EnumType.update] methods:

```python
>>> Color.add_member("BLACK", 0)
<Color.BLACK: 0>
>>> Color.update(WHITE=4)
>>> (Color.BLACK, Color.WHITE)
(<Color.BLACK: 0>, <Color.WHITE: 4>)
```

## String Enumeration

[`StringEnum`][enum_extensions.enums.StringEnum] is a simple type derived from
[`Enum`][enum_extensions.enums.Enum] and [`str`][str], which only affects
[`enum_generate_next_value`][enum_extensions.enums.enum_generate_next_value] by
making it use the case-folded version of the member name:

```python
class Status(StringEnum):
    OK = auto()

ok = Status.OK  # <Status.OK: ok>
```

Any operations derived from [`str`][str] will force members to lose their membership:

```python
title = Status.OK.title()  # Ok
```

## Integer Enumeration

[`IntEnum`][enum_extensions.enums.IntEnum] is an enumeration derived from
[`Enum`][enum_extensions.enums.Enum] and [`int`][int], which allows its members to act as integers:

```python
class Color(IntEnum):
    RED = 1
    GREEN = 2
    BLUE = 3

red = Color.RED  # <Color.RED: 1>
value = red + 2  # 3
```

Note how members also lose their membership when [`int`][int] operations are applied.

## Enforcing (Non-)Members

One can combine [`Member`][enum_extensions.members.Member] and
[`NonMember`][enum_extensions.members.NonMember] types to force members to be included or excluded
via [`member`][enum_extensions.members.member] and
[`non_member`][enum_extensions.members.non_member] functions, respectively.

Using [`member`][enum_extensions.members.member] to enforce membership:

```python
def identity(item: T) -> T:
    return item

class Function(Enum):
    IDENTITY = member(identity)

function = Function.IDENTITY  # <Function.IDENTITY: <function identity at ...>>
```

Removing the call above changes the behavior:

```python
function = Function.IDENTITY  # <function identity at ...>
```

Applying [`non_member`][enum_extensions.members.non_member] to protect items from becoming members:

```python
class Test(Enum):
    TEST = non_member(42)

test = Test.TEST  # 42
```

Removing the call above alters the behavior:

```python
class Test(Enum):
    TEST = 42

test = Test.TEST  # <Test.TEST: 42>
```
