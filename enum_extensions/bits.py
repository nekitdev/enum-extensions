from typing import Iterator

__all__ = ("bin", "bit_at", "bit_count", "bit_mask", "is_single_bit", "iter_bits")


def is_single_bit(value: int) -> bool:
    if not value:
        return False

    return not value & value - 1


def bit_at(index: int) -> int:
    return 1 << index


def bit_mask(length: int) -> int:
    return (1 << length) - 1


def bit_count(value: int) -> int:
    count = 0

    while value:
        count += 1

        value &= value - 1

    return count


def iter_bits(value: int) -> Iterator[int]:
    while value:
        bit = value & (~value + 1)

        yield bit

        value ^= bit


DIGITS = "{value:0>{length}b}"
BINARY = "0b{sign} {digits:{sign}>{bits}}"


def bin(value: int, bits: int = 0) -> str:
    length = value.bit_length()

    sign = 0

    if value < 0:
        sign = 1

        value = ~value ^ bit_mask(length)

    digits = DIGITS.format(value=value, length=length)

    return BINARY.format(sign=sign, digits=digits, bits=bits)
