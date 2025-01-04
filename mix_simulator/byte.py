from collections.abc import Sequence
from typing import List


class Byte:
    def __init__(self, val: int) -> None:
        if val >= 64:
            raise ValueError("Byte can only represent up to 6 bits")

        self.val = val

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Byte):
            return self.val == other.val
        if isinstance(other, int):
            return self.val == other

        raise TypeError(f"Cannot compare Byte to {type(other)}")


def int_to_bytes(val: int) -> List[Byte]:
    result: List[Byte] = []

    while val:
        b = Byte(val & 0b111111)
        result.append(b)
        val >>= 6

    return result


def bytes_to_int(bs: Sequence[Byte]) -> int:
    result = 0

    for i, b in enumerate(bs):
        result += b.val << (6 * i)

    return result
