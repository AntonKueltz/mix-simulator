from dataclasses import dataclass
from typing import Tuple

from mix_simulator.byte import Byte

BYTES_IN_WORD = 5


@dataclass
class Word:
    """A computer word consusts of five (six bit) bytes and a sign.

    +-----+------+------+------+------+------+
    |  0  |   1  |   2  |   3  |   4  |   5  |
    +-----+------+------+------+------+------+
    | +/- | Byte | Byte | Byte | Byte | Byte |
    +-----+------+------+------+------+------+
    """

    sign: bool
    b1: Byte
    b2: Byte
    b3: Byte
    b4: Byte
    b5: Byte

    def update(self, i: int, b: Byte) -> None:
        match i:
            case 1:
                self.b1 = b
            case 2:
                self.b2 = b
            case 3:
                self.b3 = b
            case 4:
                self.b4 = b
            case 5:
                self.b5 = b
            case _:
                raise IndexError(f"{i} is not a valid word index")

    def load_fields(self, lo: int, hi: int) -> Tuple[bool, Tuple[Byte, ...]]:
        sign = self.sign if lo == 0 else False
        lo = max(0, lo - 1)
        data = (self.b1, self.b2, self.b3, self.b4, self.b5)[lo:hi]

        return sign, data

    def compare_fields(self, lo: int, hi: int) -> Tuple[bool, Tuple[Byte, ...]]:
        return self.load_fields(lo, hi)
