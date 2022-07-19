from enum_extensions.bits import bin, bit_at, bit_count, bit_mask, is_single_bit, iter_bits

INDEX = 4


def standard_bit_at(index: int) -> int:
    return 1 << index


BIT_AT = standard_bit_at(INDEX)

BIT_MASK = BIT_AT - 1

BITS = tuple(standard_bit_at(index) for index in range(INDEX))

ZERO = 0


def test_is_single_bit() -> None:
    assert not is_single_bit(ZERO)
    assert is_single_bit(BIT_AT)
    assert not is_single_bit(BIT_MASK)


def test_bit_at() -> None:
    assert bit_at(INDEX) == BIT_AT


def test_bit_mask() -> None:
    assert bit_mask(INDEX) == BIT_MASK


def test_bit_count() -> None:
    assert not bit_count(ZERO)
    assert bit_count(BIT_MASK) == INDEX


def test_iter_bits() -> None:
    assert tuple(iter_bits(BIT_MASK)) == BITS


BINARY = "b"
SPACE = " "

BASE = 2


class TestBinary:
    RANGE = range(0, 1 << 10)

    def parse(
        self, string: str, space: str = SPACE, binary: str = BINARY, base: int = BASE
    ) -> int:
        prefix_string, _, value_string = string.partition(space)

        length = len(value_string)
        value = int(value_string, base)

        _, _, sign_string = prefix_string.partition(binary)

        sign = int(sign_string, base)

        return -(sign << length) + value

    def test_binary(self) -> None:
        for item in self.RANGE:
            for binary in (item, ~item):
                string = bin(binary)

                assert self.parse(string) == binary
