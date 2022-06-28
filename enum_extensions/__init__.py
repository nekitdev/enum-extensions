"""Enhanced enumerations for Python.

# Example

```python
# color.py
from enum_extensions import Enum

class Color(Enum):
    ALPHA = 0
    RED = 1
    GREEN = 2
    BLUE = 3
```

```python
>>> from color import Color
>>> Color
<enum `Color`>
>>> Color.RED  # attribute access
<Color.RED: 1>
>>> Color["GREEN"]  # name access
<Color.GREEN: 2>
>>> Color(3)  # value access
<Color.BLUE: 3>
>>> color = Color.from_name("alpha")  # caseless name access
>>> print(color.name)
ALPHA
>>> print(color.value)
0
>>> print(color.title_name)
Alpha
```
"""

__description__ = "Enhanced enumerations for Python."
__url__ = "https://github.com/nekitdev/enum_extensions"

__title__ = "enum_extensions"
__author__ = "nekitdev"
__license__ = "MIT"
__version__ = "0.1.0"

from enum_extensions.auto import Auto, auto, is_auto
from enum_extensions.enums import (
    Enum,
    EnumType,
    IntEnum,
    StringEnum,
    enum_generate_next_value,
    is_enum,
    is_enum_member,
)
from enum_extensions.flags import (
    CONFORM,
    KEEP,
    STRICT,
    Flag,
    FlagBoundary,
    FlagType,
    IntFlag,
    is_flag,
    is_flag_member,
)
from enum_extensions.members import Member, NonMember, is_member, is_non_member, member, non_member
from enum_extensions.traits import FormatTrait, OrderTrait, TitleTrait, Trait

__all__ = (
    "Auto",
    "auto",
    "is_auto",
    "enum_generate_next_value",
    "EnumType",
    "Enum",
    "IntEnum",
    "StringEnum",
    "is_enum",
    "is_enum_member",
    "STRICT",
    "CONFORM",
    "KEEP",
    "FlagBoundary",
    "FlagType",
    "Flag",
    "IntFlag",
    "is_flag",
    "is_flag_member",
    "Member",
    "NonMember",
    "member",
    "non_member",
    "is_member",
    "is_non_member",
    "FormatTrait",
    "OrderTrait",
    "TitleTrait",
    "Trait",
)
