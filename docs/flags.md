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
more fine-grained control over how invalid values are dealt with in
[`Flag`][enum_extensions.flags.Flag] types.
