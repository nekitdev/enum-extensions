# Flags

## Prerequisites

Code snippets and examples below are using several common imports and types,
which are mainly omitted for simplicity:

```python
from typing import TypeVar  # for various typing purposes

from enum_extensions import (  # library imports used in examples
    # flag boundary
    FlagBoundary,
    # boundaries
    CONFORM,
    KEEP,
    STRICT,
    # flags
    Flag,
    IntFlag,
    # auto items
    auto,
)

F = TypeVar("F", bound=Flag)  # flag type variable
```

## [`FlagBoundary`][enum_extensions.flags.FlagBoundary]

[`FlagBoundary`][enum_extensions.flags.FlagBoundary] is an enumeration
with the values `STRICT`, `CONFORM` and `KEEP` which allows for
more fine-grained control over how *invalid* (or, rather, *out-of-range*)
values are dealt with in [`Flag`][enum_extensions.flags.Flag] types.

### `STRICT`

*Out-of-range* values cause [`ValueError`][ValueError].
This is the default for [`Flag`][enum_extensions.flags.Flag].

```python
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

### `CONFORM`

*Out-of-range* values have invalid values removed, leaving a valid
[`Flag`][enum_extensions.flags.Flag] member.

```python
class ConformFlag(Flag, boundary=CONFORM):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
```

```python
>>> ConformFlag((1 << 2) + (1 << 4))
<ConformFlag.BLUE: 4>
```

### `KEEP`

*Out-of-range* values are kept along with the
[`Flag`][enum_extensions.flags.Flag] membership.
This is the default for [`IntFlag`][enum_extensions.flags.IntFlag].

```python
class KeepFlag(Flag, boundary=KEEP):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
```

```python
>>> KeepFlag((1 << 2) + (1 << 4))
<KeepFlag.BLUE|0x10: 4>
```

## [`Flag`][enum_extensions.flags.Flag]

[`Flag`][enum_extensions.flags.Flag] is a special [`Enum`][enum_extensions.enums.Enum]
focused around supporting *bit-flags* along with operations on them, such as `&` (*AND*),
`|` (*OR*), `^` (*XOR*) and `~` (*INVERT*).

```python
from enum_extensions import Flag

class P(Flag):
    N = 0
    X = 1
    W = 2
    R = 4

RW = P.R | P.W  # <P.W|R: 6>

RWX = ~P.N  # <P.X|W|R: 7>

RX = RWX ^ P.W  # <P.X|R: 5>

N = RWX & P.N  # <P.N: 0>
```

## Iteration

## Length

Flag members know the number of bits in them:

```python
>>> len(RWX)
3
```

## Non-Zero Checks

Calling [`bool`][bool] on the [`Flag`][enum_extensions.flags.Flag] member can be used to check
if the member is non-zero:

```python
>>> bool(RW)
True
>>> bool(N)
False
```

## Container Checks

Flags can check if the member belongs to another member:

```python
>>> P.R in RW
True
>>> P.N in RWX
False
```

## [`IntFlag`][enum_extensions.flags.IntFlag]

[`IntFlag`][enum_extensions.flags.IntFlag] is a flag derived from
[`Flag`][enum_extensions.flags.Flag] and [`int`][int], which allows its members to act as integers:

```python
class Color(IntFlag):
    RED = 1
    GREEN = 2
    BLUE = 4

red = Color.RED  # <Color.RED: 1>
value = red + 2  # 3
```

Note how members also lose their membership when [`int`][int] operations are applied.

[`IntFlag`][enum_extensions.flags.IntFlag] members can be combined with integer values
(compared to [`Flag`][enum_extensions.flags.Flag] which only supports checking members):

```python
red = Color.RED  # <Color.RED: 1>
red_blue = red | 4  # <Color.RED|BLUE: 4>
```
