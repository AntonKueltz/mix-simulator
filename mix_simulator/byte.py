from collections.abc import Iterable
from typing import List

BITS_IN_BYTE = 6
UPPER_LIMIT = 1 << BITS_IN_BYTE
BIT_MASK = UPPER_LIMIT - 1


class Byte:
    """A basic unit of information capable of holding 64 distinct values."""

    def __init__(self, val: int) -> None:
        if val >= UPPER_LIMIT:
            raise ValueError(f"Byte can only represent up to {BITS_IN_BYTE} bits")

        self.val = val

    def __repr__(self) -> str:
        return f"Byte({self.val})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Byte):
            return self.val == other.val
        if isinstance(other, int):
            return self.val == other

        raise TypeError(f"Cannot compare Byte to {type(other)}")


def int_to_bytes(val: int, padding: int = 0) -> List[Byte]:
    val = abs(val)
    result: List[Byte] = []

    while val:
        b = Byte(val & BIT_MASK)
        result.append(b)
        val >>= BITS_IN_BYTE
        padding -= 1

    while padding > 0:
        result.append(Byte(0))
        padding -= 1

    return result


def bytes_to_int(bs: Iterable[Byte], sign: bool = False) -> int:
    result = 0

    for i, b in enumerate(bs):
        result += b.val << (BITS_IN_BYTE * i)

    return -result if sign else result
