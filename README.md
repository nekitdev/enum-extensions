# `enum-extensions`

[![License][License Badge]][License]
[![Version][Version Badge]][Package]
[![Downloads][Downloads Badge]][Package]
[![Discord][Discord Badge]][Discord]

<!--
[![Check][Check Badge]][Actions]
-->
[![Documentation][Documentation Badge]][Documentation]
[![Test][Test Badge]][Actions]
[![Coverage][Coverage Badge]][Coverage]

**Enhanced enumerations for Python.**

## Installing

**Python 3.7 or above is required.**

### pip

Installing the library with `pip` is quite simple:

```console
$ pip install enum-extensions
```

Alternatively, the library can be installed from source:

```console
$ git clone https://github.com/nekitdev/enum-extensions.git
$ cd enum-extensions
$ python -m pip install .
```

### poetry

You can add `enum-extensions` as a dependency with the following command:

```console
$ poetry add enum-extensions
```

Or by directly specifying it in the configuration like so:

```toml
[tool.poetry.dependencies]
enum-extensions = "^0.1.0"
```

Alternatively, you can add it directly from the source:

```toml
[tool.poetry.dependencies.enum-extensions]
git = "https://github.com/nekitdev/enum-extensions.git"
```

## Examples

Creating a simple enumeration:

```python
from enum_extensions import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

Accessing members by name or by value:

```python
red = Color.RED  # <Color.RED: 1>
green = Color["GREEN"]  # <Color.GREEN: 2>
blue = Color(3)  # <Color.BLUE>
```

## Documentation

You can find the documentation [here][Documentation].

## Support

If you need support with the library, you can send an [email][Email]
or refer to the official [Discord server][Discord].

## Changelog

You can find the changelog [here][Changelog].

## Security Policy

You can find the Security Policy of `enum-extensions` [here][Security].

## Contributing

If you are interested in contributing to `enum-extensions`, make sure to take a look at the
[Contributing Guide][Contributing Guide], as well as the [Code of Conduct][Code of Conduct].

## License

`enum-extensions` is licensed under the MIT License terms. See [License][License] for details.

[Email]: mailto:support@nekit.dev

[Discord]: https://nekit.dev/discord

[Actions]: https://github.com/nekitdev/enum-extensions/actions

[Changelog]: https://github.com/nekitdev/enum-extensions/blob/main/CHANGELOG.md
[Code of Conduct]: https://github.com/nekitdev/enum-extensions/blob/main/CODE_OF_CONDUCT.md
[Contributing Guide]: https://github.com/nekitdev/enum-extensions/blob/main/CONTRIBUTING.md
[Security]: https://github.com/nekitdev/enum-extensions/blob/main/SECURITY.md

[License]: https://github.com/nekitdev/enum-extensions/blob/main/LICENSE

[Package]: https://pypi.org/project/enum-extensions
[Coverage]: https://codecov.io/gh/nekitdev/enum-extensions
[Documentation]: https://nekitdev.github.io/enum-extensions

[Discord Badge]: https://img.shields.io/badge/chat-discord-5865f2
[License Badge]: https://img.shields.io/pypi/l/enum-extensions
[Version Badge]: https://img.shields.io/pypi/v/enum-extensions
[Downloads Badge]: https://img.shields.io/pypi/dm/enum-extensions

[Documentation Badge]: https://github.com/nekitdev/enum-extensions/workflows/docs/badge.svg
[Check Badge]: https://github.com/nekitdev/enum-extensions/workflows/check/badge.svg
[Test Badge]: https://github.com/nekitdev/enum-extensions/workflows/test/badge.svg
[Coverage Badge]: https://codecov.io/gh/nekitdev/enum-extensions/branch/main/graph/badge.svg
