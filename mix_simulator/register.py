from __future__ import annotations
from typing import Tuple

from mix_simulator.byte import Byte, bytes_to_int
from mix_simulator.word import BYTES_IN_WORD


class WordRegister:
    BYTES: int = 5

    sign: bool
    r1: Byte
    r2: Byte
    r3: Byte
    r4: Byte
    r5: Byte

    def __init__(
        self, sign: bool, r1: Byte, r2: Byte, r3: Byte, r4: Byte, r5: Byte
    ) -> None:
        self.sign = sign
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.r5 = r5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WordRegister):
            raise NotImplementedError(
                "Can only compare WordRegister to other WordRegisters"
            )

        return (
            self.sign == other.sign
            and self.r1 == other.r1
            and self.r2 == other.r2
            and self.r3 == other.r3
            and self.r4 == other.r4
            and self.r5 == other.r5
        )

    def __int__(self) -> int:
        return bytes_to_int((self.r1, self.r2, self.r3, self.r4, self.r5), self.sign)

    def __repr__(self) -> str:
        return f"WordRegister({'-' if self.sign else '+'} {self.r1} {self.r2} {self.r3} {self.r4} {self.r5})"

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


class IndexRegister:
    BYTES: int = 2

    sign: bool
    i4: Byte
    i5: Byte

    def __init__(self, sign: bool, i4: Byte, i5: Byte) -> None:
        self.sign = sign
        self.i4 = i4
        self.i5 = i5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IndexRegister):
            raise NotImplementedError(
                "Can only compare IndexRegister to other IndexRegisters"
            )

        return self.sign == other.sign and self.i4 == other.i4 and self.i5 == other.i5

    def __int__(self) -> int:
        return bytes_to_int((self.i4, self.i5), self.sign)

    def __repr__(self) -> str:
        return f"IndexRegister({'-' if self.sign else '+'} {self.i4} {self.i5})"

    def update(self, sign: bool, i5: Byte = Byte(0), i4: Byte = Byte(0)) -> None:
        self.sign = sign
        self.i5 = i5
        self.i4 = i4

    def store_fields(self, lo: int, hi: int) -> Tuple[bool | None, Tuple[Byte, ...]]:
        sign = self.sign if lo == 0 else None
        lo = max(1, lo)
        count = hi - lo + 1
        full_word = (Byte(0),) * (BYTES_IN_WORD - 2) + (self.i4, self.i5)
        data = full_word[-count:]

        return sign, data


class JumpRegister:
    BYTES: int = 2

    j4: Byte
    j5: Byte

    def __init__(self, j4: Byte, j5: Byte) -> None:
        self.j4 = j4
        self.j5 = j5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JumpRegister):
            raise NotImplementedError(
                "Can only compare JumpRegister to other JumpRegisters"
            )

        return self.j4 == other.j4 and self.j5 == other.j5

    def __int__(self) -> int:
        return bytes_to_int((self.j4, self.j5), False)

    def __repr__(self) -> str:
        return f"JumpRegister(+ {self.j4} {self.j5})"

    def update(self, j5: Byte = Byte(0), j4: Byte = Byte(0)) -> None:
        self.j5 = j5
        self.j4 = j4

    def store_fields(self, lo: int, hi: int) -> Tuple[bool | None, Tuple[Byte, ...]]:
        sign = False if lo == 0 else None
        lo = max(1, lo)
        count = hi - lo + 1
        full_word = (Byte(0),) * (BYTES_IN_WORD - 2) + (self.j4, self.j5)
        data = full_word[-count:]

        return sign, data


ZERO_REGISTER = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
