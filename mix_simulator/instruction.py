from __future__ import annotations
from typing import Tuple

from mix_simulator.byte import (
    BITS_IN_BYTE,
    BYTE_UPPER_LIMIT,
    Byte,
    bytes_to_int,
    int_to_bytes,
)
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.opcode import OpCode
from mix_simulator.register import (
    ZERO_REGISTER,
    IndexRegister,
    JumpRegister,
    WordRegister,
)
from mix_simulator.simulator import STATE
from mix_simulator.word import BYTES_IN_WORD, Word


class Instruction:
    """An instruction that can be executed by the simulator."""

    address: int
    index: int
    field: int
    modification: Tuple[int, int]
    opcode: OpCode

    def __init__(self, address: int, index: int, field: int, opcode: OpCode) -> None:
        self.address = address
        self.index = index
        self.field = field
        self.modification = divmod(self.field, 8)
        self.opcode = opcode

    @staticmethod
    def from_word(word: Word) -> Instruction:
        address = bytes_to_int((word.b1, word.b2))
        if word.sign:
            address *= -1

        index = word.b3.val
        field = word.b4.val
        opcode = OpCode(word.b5.val)

        return Instruction(address, index, field, opcode)

    def execute(self) -> None:
        match self.opcode:
            # Arithmetic
            case OpCode.ADD:
                self._add()
            case OpCode.SUB:
                self._add(negative=True)
            case OpCode.MUL:
                self._mul()
            case OpCode.DIV:
                self._div()

            # LD*
            case OpCode.LDA:
                self._load(STATE.rA)
            case OpCode.LDX:
                self._load(STATE.rX)
            case OpCode.LD1:
                self._load(STATE.rI1)
            case OpCode.LD2:
                self._load(STATE.rI2)
            case OpCode.LD3:
                self._load(STATE.rI3)
            case OpCode.LD4:
                self._load(STATE.rI4)
            case OpCode.LD5:
                self._load(STATE.rI5)
            case OpCode.LD6:
                self._load(STATE.rI6)

            # LD*N
            case OpCode.LDAN:
                self._load(STATE.rA, negative=True)
            case OpCode.LDXN:
                self._load(STATE.rX, negative=True)
            case OpCode.LD1N:
                self._load(STATE.rI1, negative=True)
            case OpCode.LD2N:
                self._load(STATE.rI2, negative=True)
            case OpCode.LD3N:
                self._load(STATE.rI3, negative=True)
            case OpCode.LD4N:
                self._load(STATE.rI4, negative=True)
            case OpCode.LD5N:
                self._load(STATE.rI5, negative=True)
            case OpCode.LD6N:
                self._load(STATE.rI6, negative=True)

            # ST*
            case OpCode.STA:
                self._store(STATE.rA)
            case OpCode.STX:
                self._store(STATE.rX)
            case OpCode.ST1:
                self._store(STATE.rI1)
            case OpCode.ST2:
                self._store(STATE.rI2)
            case OpCode.ST3:
                self._store(STATE.rI3)
            case OpCode.ST4:
                self._store(STATE.rI4)
            case OpCode.ST5:
                self._store(STATE.rI5)
            case OpCode.ST6:
                self._store(STATE.rI6)
            case OpCode.STJ:
                self._store(STATE.rJ)
            case OpCode.STZ:
                self._store(ZERO_REGISTER)

            # ENT* / ENN* / INC* / DEC*
            case OpCode.ATA:
                self._address_transfer(STATE.rA)
            case OpCode.ATX:
                self._address_transfer(STATE.rX)
            case OpCode.AT1:
                self._address_transfer(STATE.rI1)
            case OpCode.AT2:
                self._address_transfer(STATE.rI2)
            case OpCode.AT3:
                self._address_transfer(STATE.rI3)
            case OpCode.AT4:
                self._address_transfer(STATE.rI4)
            case OpCode.AT5:
                self._address_transfer(STATE.rI5)
            case OpCode.AT6:
                self._address_transfer(STATE.rI6)

            # CMP*
            case OpCode.CMPA:
                self._compare(STATE.rA)
            case OpCode.CMPX:
                self._compare(STATE.rX)
            case OpCode.CMP1:
                self._compare(STATE.rI1)
            case OpCode.CMP2:
                self._compare(STATE.rI2)
            case OpCode.CMP3:
                self._compare(STATE.rI3)
            case OpCode.CMP4:
                self._compare(STATE.rI4)
            case OpCode.CMP5:
                self._compare(STATE.rI5)
            case OpCode.CMP6:
                self._compare(STATE.rI6)

            # J*
            case OpCode.JMP:
                self._jump(None)
            case OpCode.JA:
                self._jump(STATE.rA)
            case OpCode.JX:
                self._jump(STATE.rX)
            case OpCode.J1:
                self._jump(STATE.rI1)
            case OpCode.J2:
                self._jump(STATE.rI2)
            case OpCode.J3:
                self._jump(STATE.rI3)
            case OpCode.J4:
                self._jump(STATE.rI4)
            case OpCode.J5:
                self._jump(STATE.rI5)
            case OpCode.J6:
                self._jump(STATE.rI6)

            # S*
            case OpCode.SH:
                self._shift()

            # Unknown OpCode
            case _:
                raise ValueError(f"Unsupported opcode {self.opcode}")

    def _load(
        self, register: IndexRegister | WordRegister, negative: bool = False
    ) -> None:
        # load word at address
        m = self._get_address()
        word = STATE.memory[m]

        # select relevant fields
        sign, data = word.load_fields(*self.modification)

        # LDi is invalid if setting any of the upper 3 bytes
        if isinstance(register, IndexRegister) and len(data) > 2:
            raise ValueError(
                "The LDi instruction is undefined if it would result in setting bytes 1, 2 or 3 to anything but zero."
            )

        if negative:
            sign = not sign

        # set the value
        # flip the endianness of the data since the update function uses little endian
        little_endian_data = reversed(data)
        register.update(sign, *little_endian_data)

    def _store(self, register: IndexRegister | JumpRegister | WordRegister) -> None:
        # get data from register
        sign, data = register.store_fields(*self.modification)

        # get the word to update
        m = self._get_address()
        word = STATE.memory[m]

        # store the data in the word
        if sign is not None:
            word.sign = sign

        # look at the range of l:r that we need to insert in
        # l must start at 1, since 0 is the sign index
        lo, hi = self.modification
        indices = range(max(lo, 1), hi + 1)
        for i, d in zip(indices, data):
            word.update(i, d)

    def _add(self, negative: bool = False) -> None:
        # load the value in the instruction as an integer
        m = self._get_address()
        word = STATE.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # add V to A
        a = int(STATE.rA)
        a += -v if negative else v

        # store back into A
        sign, result = int_to_bytes(a, padding=STATE.rA.BYTES)

        if len(result) == STATE.rA.BYTES + 1:
            STATE.overflow = True
            result = result[: STATE.rA.BYTES]

        STATE.rA.update(sign, *result)

    def _mul(self) -> None:
        # load the value in the instruction as an integer
        m = self._get_address()
        word = STATE.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # multiple A by V
        a = int(STATE.rA)
        product = a * v

        # store back into A and X
        sign, result = int_to_bytes(product, padding=STATE.rA.BYTES + STATE.rX.BYTES)
        # X gets the low bytes
        STATE.rX.update(sign, *result[: STATE.rX.BYTES])
        # A gets the high bytes
        STATE.rA.update(sign, *result[STATE.rX.BYTES :])

    def _div(self) -> None:
        # load the value in the instruction as an integer
        m = self._get_address()
        word = STATE.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # divide AX by V
        a = int(STATE.rA)
        x = int(STATE.rX)
        ax = (abs(a) << (BYTES_IN_WORD * BITS_IN_BYTE)) + abs(x)
        ax = -ax if a < 0 else ax
        quotient, remainder = divmod(ax, v)
        sign = sign != STATE.rA.sign

        # store quotient back into A
        _, result = int_to_bytes(quotient, padding=STATE.rA.BYTES)
        if len(result) > STATE.rA.BYTES:
            STATE.overflow = True
            result = result[: STATE.rA.BYTES]
        STATE.rA.update(sign, *result)

        # store remainder back into X
        _, result = int_to_bytes(remainder, padding=STATE.rX.BYTES)
        STATE.rX.update(sign, *result)

    def _address_transfer(self, register: IndexRegister | WordRegister) -> None:
        match self.field:
            case 0:
                self._increment(register)
            case 1:
                self._increment(register, negative=True)
            case 2:
                self._enter(register)
            case 3:
                self._enter(register, negative=True)
            case _:
                raise ValueError(
                    f"{self.field} is not a valid op variant for an address transfer operator."
                )

    def _enter(
        self, register: IndexRegister | WordRegister, negative: bool = False
    ) -> None:
        # TODO - does not support -0 currently

        # get the value of the address and interpret it as an integer
        m = self._get_address()
        sign, data = int_to_bytes(m)

        # flip the sign if negative
        if negative:
            sign = not sign

        # set the relevant register
        register.update(sign, *data)

    def _increment(
        self, register: IndexRegister | WordRegister, negative: bool = False
    ) -> None:
        # compute increment / decrement
        m = self._get_address()
        i = int(register)
        i += -m if negative else m

        # store back into register
        sign, result = int_to_bytes(i, padding=register.BYTES)

        if len(result) == register.BYTES + 1:
            STATE.overflow = True
            result = result[: register.BYTES]

        register.update(sign, *result)

    def _compare(self, register: IndexRegister | WordRegister) -> None:
        # an equal comparison always occurs when F is (0:0)
        if self.field == 0:
            STATE.comparison_indicator = ComparisonIndicator.EQUAL
            return

        # load word at address
        m = self._get_address()
        word = STATE.memory[m]

        # select relevant fields
        lsign, ldata = register.compare_fields(*self.modification)
        rsign, rdata = word.compare_fields(*self.modification)

        # compare the values
        left = bytes_to_int(ldata, lsign)
        right = bytes_to_int(rdata, rsign)

        if left < right:
            STATE.comparison_indicator = ComparisonIndicator.LESS
        elif left == right:
            STATE.comparison_indicator = ComparisonIndicator.EQUAL
        else:
            STATE.comparison_indicator = ComparisonIndicator.GREATER

    def _jump(self, register: IndexRegister | WordRegister | None) -> None:
        criteria_met = False

        # evaluate the jump criteria
        if self.opcode == OpCode.JMP:
            # JMP and JSP
            if self.field == 0 or self.field == 1:
                criteria_met = True
            # JOV - if the overflow toggle is on, it is turned off and a JMP occurs
            elif self.field == 2 and STATE.overflow:
                criteria_met = True
                STATE.overflow = False
            # JNOV - if the overflow toggle is off, a JMP occurs; otherwise it is turned off
            elif self.field == 3:
                if not STATE.overflow:
                    criteria_met = True
                else:
                    STATE.overflow = False
            # JL
            elif (
                self.field == 4
                and STATE.comparison_indicator == ComparisonIndicator.LESS
            ):
                criteria_met = True
            # JE
            elif (
                self.field == 5
                and STATE.comparison_indicator == ComparisonIndicator.EQUAL
            ):
                criteria_met = True
            # JG
            elif (
                self.field == 6
                and STATE.comparison_indicator == ComparisonIndicator.GREATER
            ):
                criteria_met = True
            # JGE
            elif (
                self.field == 7
                and STATE.comparison_indicator != ComparisonIndicator.LESS
            ):
                criteria_met = True
            # JNE
            elif (
                self.field == 8
                and STATE.comparison_indicator != ComparisonIndicator.EQUAL
            ):
                criteria_met = True
            # JLE
            elif (
                self.field == 9
                and STATE.comparison_indicator != ComparisonIndicator.GREATER
            ):
                criteria_met = True
        elif register is not None:
            val = int(register)
            # J*N
            if self.field == 0 and val < 0:
                criteria_met = True
            # J*Z
            elif self.field == 1 and val == 0:
                criteria_met = True
            # J*P
            elif self.field == 2 and val > 0:
                criteria_met = True
            # J*NN
            elif self.field == 3 and val >= 0:
                criteria_met = True
            # J*NZ
            elif self.field == 4 and val != 0:
                criteria_met = True
            # J*NP
            elif self.field == 5 and val <= 0:
                criteria_met = True

        if not criteria_met:
            return

        # update J (JSJ does not update J)
        if self.opcode != OpCode.JMP or self.field != 1:
            # program counter containes the _next_ instruction (word)
            hi, lo = divmod(STATE.program_counter, BYTE_UPPER_LIMIT)
            STATE.rJ.update(Byte(lo), Byte(hi))

        # perform the jump
        STATE.program_counter = self._get_address()

    def _shift(self) -> None:
        m = self._get_address()
        if m < 0:
            raise ValueError(f"Cannot shift by a negative amount ({m})")

        # reduce m by the amount of bytes in the register(s) to circular shift
        if self.field == 4 or self.field == 5:
            m %= STATE.rA.BYTES + STATE.rX.BYTES
        # shift by 0 is a NOP
        if m == 0:
            return
        bits_to_shift = BITS_IN_BYTE * m

        # SLA and SRA
        if self.field == 0 or self.field == 1:
            if m >= STATE.rA.BYTES:
                # all bytes were shifted out of A
                data = [Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)]
            else:
                a = abs(int(STATE.rA))
                new_value = (
                    a << bits_to_shift if self.field == 0 else a >> bits_to_shift
                )
                _, data = int_to_bytes(new_value)

            # set A
            STATE.rA.update(STATE.rA.sign, *data[: STATE.rA.BYTES])
        # SLAX and SRAX
        elif self.field == 2 or self.field == 3:
            if m >= STATE.rA.BYTES + STATE.rX.BYTES:
                # all bytes were shifted out of A and X
                data = [
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                    Byte(0),
                ]
            else:
                ax = (abs(int(STATE.rA)) << (BITS_IN_BYTE * STATE.rA.BYTES)) + abs(
                    (int(STATE.rX))
                )
                new_value = (
                    ax << bits_to_shift if self.field == 2 else ax >> bits_to_shift
                )
                _, data = int_to_bytes(new_value)
                data = data[: STATE.rA.BYTES + STATE.rX.BYTES]

            # set A and X
            STATE.rX.update(STATE.rX.sign, *data[: STATE.rX.BYTES])
            STATE.rA.update(STATE.rA.sign, *data[STATE.rX.BYTES :])
        # SLC and SRC
        elif self.field == 4 or self.field == 5:
            rx, ra = STATE.rX, STATE.rA
            # little endian representation of AX
            data = [
                rx.r5,
                rx.r4,
                rx.r3,
                rx.r2,
                rx.r1,
                ra.r5,
                ra.r4,
                ra.r3,
                ra.r2,
                ra.r1,
            ]
            ln = len(data)

            # circular shift the data
            shifted = []
            for i in range(ln):
                j = (i - m) % ln if self.field == 4 else (i + m) % ln
                shifted.append(data[j])

            # set A and X
            STATE.rX.update(STATE.rX.sign, *shifted[: STATE.rX.BYTES])
            STATE.rA.update(STATE.rA.sign, *shifted[STATE.rX.BYTES :])

    def _get_address(self) -> int:
        match self.index:
            case 0:
                return self.address
            case 1:
                return self.address + int(STATE.rI1)
            case 2:
                return self.address + int(STATE.rI2)
            case 3:
                return self.address + int(STATE.rI3)
            case 4:
                return self.address + int(STATE.rI4)
            case 5:
                return self.address + int(STATE.rI5)
            case 6:
                return self.address + int(STATE.rI6)
            case _:
                raise ValueError(f"Index must be value in range 0-6. Got {self.index}")
