from dataclasses import dataclass
from typing import Tuple

from mix_simulator.byte import Byte, bytes_to_int


@dataclass
class WordRegister:
    sign: bool
    r1: Byte
    r2: Byte
    r3: Byte
    r4: Byte
    r5: Byte

    def __int__(self) -> int:
        return bytes_to_int((self.r1, self.r2, self.r3, self.r4, self.r5), self.sign)

    def update(
        self,
        sign: bool,
        r5: Byte = Byte(0),
        r4: Byte = Byte(0),
        r3: Byte = Byte(0),
        r2: Byte = Byte(0),
        r1: Byte = Byte(0),
    ) -> None:
        self.sign = sign
        self.r5 = r5
        self.r4 = r4
        self.r3 = r3
        self.r2 = r2
        self.r1 = r1

    def store_fields(self, lo: int, hi: int) -> Tuple[bool | None, Tuple[Byte, ...]]:
        sign = self.sign if lo == 0 else None
        lo = max(1, lo)
        count = hi - lo + 1
        data = (self.r1, self.r2, self.r3, self.r4, self.r5)[-count:]

        return sign, data


@dataclass
class IndexRegister:
    sign: bool
    i4: Byte
    i5: Byte

    def __int__(self) -> int:
        return bytes_to_int((self.i4, self.i5), self.sign)

    def update(self, sign: bool, i5: Byte = Byte(0), i4: Byte = Byte(0)) -> None:
        self.sign = sign
        self.i5 = i5
        self.i4 = i4

    def store_fields(self, lo: int, hi: int) -> Tuple[bool | None, Tuple[Byte, ...]]:
        sign = self.sign if lo == 0 else None
        lo = max(1, lo)
        count = hi - lo + 1
        data = (Byte(0), Byte(0), Byte(0), self.i4, self.i5)[-count:]

        return sign, data
