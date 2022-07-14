# Traits

`enum-extensions` implements special *traits* (aka *mixins*), which add specific behavior
to enumerations. Each [`Trait`][enum_extensions.traits.Trait] implements some functionality
for enumerations, but does not subclass [`Enum`][enum_extensions.enums.Enum] directly.

## Prerequisites

Code snippets and examples below are using several common imports and types,
which are mainly omitted for simplicity:

```python
from enum_extensions import (  # library imports used in examples
    # enumerations
    Enum,
    # traits
    Trait,
    Order,
    Format,
    Title,
    # auto items
    auto,
)
```

## Ordering

[`Order`][enum_extensions.traits.Order] implements ordering (`<`, `>`, `<=`, `>=`)
for enumerations:

```python
class Grade(Order, Enum):
    A = 5
    B = 4
    C = 3
    D = 2
    F = 1
```

```python
>>> Grade.F < Grade.D
True
>>> Grade.A > Grade.B
True
>>> Grade.C <= Grade.C
True
>>> Grade.B >= Grade.B
True
```

## Formatting

[`Format`][enum_extensions.traits.Format]

## Titles

[`Title`][enum_extensions.traits.Title]

## Defining Traits

One can define custom traits to use, for instance:

```python
class StringTitle(Trait):
    """Use the title of the member as its string representation."""

    def __str__(self) -> str:
        return self.title_name
```

Deriving from this new trait:

```python
class Color(StringTitle, Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
```

Gives the expected result:

```python
>>> print(Color.RED)
Red
```
