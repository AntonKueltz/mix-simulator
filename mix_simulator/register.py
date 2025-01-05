from dataclasses import dataclass

from mix_simulator.byte import Byte


@dataclass
class WordRegister:
    sign: bool
    r1: Byte
    r2: Byte
    r3: Byte
    r4: Byte
    r5: Byte

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


@dataclass
class IndexRegister:
    sign: bool
    i4: Byte
    i5: Byte

    def update(self, sign: bool, i5: Byte = Byte(0), i4: Byte = Byte(0)) -> None:
        self.sign = sign
        self.i5 = i5
        self.i4 = i4
