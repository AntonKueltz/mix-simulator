from __future__ import annotations
from typing import List, Tuple

from mix_simulator.byte import (
    BITS_IN_BYTE,
    BYTE_UPPER_LIMIT,
    Byte,
    bytes_to_int,
    int_to_bytes,
)
from mix_simulator.character_code import byte_to_char, char_to_byte
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.opcode import OpCode
from mix_simulator.operator import Operator
from mix_simulator.register import (
    ZERO_REGISTER,
    IndexRegister,
    JumpRegister,
    WordRegister,
)
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import BYTES_IN_WORD, Word

INSTRUCTION_CACHE: dict[Word, Instruction] = {}


class Instruction:
    """An instruction that can be executed by the simulator."""

    address: int
    index: int
    field: int
    modification: Tuple[int, int]
    opcode: OpCode
    state: SimulatorState

    def __init__(
        self,
        address: int,
        index: int,
        field: int,
        opcode: OpCode,
        state: SimulatorState,
    ) -> None:
        self.address = address
        self.index = index
        self.field = field
        self.modification = divmod(self.field, 8)
        self.opcode = opcode
        self.state = state

    def __repr__(self) -> str:
        op = Operator.from_code_and_field(self.opcode, self.field)
        addr = self.address
        idx = f",{self.index}" if self.index else ""
        left, right = self.modification
        lr = f"({left}:{right})" if self.field != 5 else ""

        return f"{op.name} {addr}{idx}{lr}"

    @staticmethod
    def from_word(word: Word, state: SimulatorState) -> Instruction:
        global INSTRUCTION_CACHE

        if word in INSTRUCTION_CACHE:
            instruction = INSTRUCTION_CACHE[word]
            instruction.state = state
            return instruction

        address = bytes_to_int((word.b1, word.b2))
        if word.sign:
            address *= -1

        index = word.b3.val
        field = word.b4.val
        opcode = OpCode(word.b5.val)

        instruction = Instruction(address, index, field, opcode, state)
        INSTRUCTION_CACHE[word] = instruction
        return instruction

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
                self._load(self.state.rA)
            case OpCode.LDX:
                self._load(self.state.rX)
            case OpCode.LD1:
                self._load(self.state.rI1)
            case OpCode.LD2:
                self._load(self.state.rI2)
            case OpCode.LD3:
                self._load(self.state.rI3)
            case OpCode.LD4:
                self._load(self.state.rI4)
            case OpCode.LD5:
                self._load(self.state.rI5)
            case OpCode.LD6:
                self._load(self.state.rI6)

            # LD*N
            case OpCode.LDAN:
                self._load(self.state.rA, negative=True)
            case OpCode.LDXN:
                self._load(self.state.rX, negative=True)
            case OpCode.LD1N:
                self._load(self.state.rI1, negative=True)
            case OpCode.LD2N:
                self._load(self.state.rI2, negative=True)
            case OpCode.LD3N:
                self._load(self.state.rI3, negative=True)
            case OpCode.LD4N:
                self._load(self.state.rI4, negative=True)
            case OpCode.LD5N:
                self._load(self.state.rI5, negative=True)
            case OpCode.LD6N:
                self._load(self.state.rI6, negative=True)

            # ST*
            case OpCode.STA:
                self._store(self.state.rA)
            case OpCode.STX:
                self._store(self.state.rX)
            case OpCode.ST1:
                self._store(self.state.rI1)
            case OpCode.ST2:
                self._store(self.state.rI2)
            case OpCode.ST3:
                self._store(self.state.rI3)
            case OpCode.ST4:
                self._store(self.state.rI4)
            case OpCode.ST5:
                self._store(self.state.rI5)
            case OpCode.ST6:
                self._store(self.state.rI6)
            case OpCode.STJ:
                self._store(self.state.rJ)
            case OpCode.STZ:
                self._store(ZERO_REGISTER)

            # ENT* / ENN* / INC* / DEC*
            case OpCode.ATA:
                self._address_transfer(self.state.rA)
            case OpCode.ATX:
                self._address_transfer(self.state.rX)
            case OpCode.AT1:
                self._address_transfer(self.state.rI1)
            case OpCode.AT2:
                self._address_transfer(self.state.rI2)
            case OpCode.AT3:
                self._address_transfer(self.state.rI3)
            case OpCode.AT4:
                self._address_transfer(self.state.rI4)
            case OpCode.AT5:
                self._address_transfer(self.state.rI5)
            case OpCode.AT6:
                self._address_transfer(self.state.rI6)

            # CMP*
            case OpCode.CMPA:
                self._compare(self.state.rA)
            case OpCode.CMPX:
                self._compare(self.state.rX)
            case OpCode.CMP1:
                self._compare(self.state.rI1)
            case OpCode.CMP2:
                self._compare(self.state.rI2)
            case OpCode.CMP3:
                self._compare(self.state.rI3)
            case OpCode.CMP4:
                self._compare(self.state.rI4)
            case OpCode.CMP5:
                self._compare(self.state.rI5)
            case OpCode.CMP6:
                self._compare(self.state.rI6)

            # J*
            case OpCode.JMP:
                self._jump(None)
            case OpCode.JA:
                self._jump(self.state.rA)
            case OpCode.JX:
                self._jump(self.state.rX)
            case OpCode.J1:
                self._jump(self.state.rI1)
            case OpCode.J2:
                self._jump(self.state.rI2)
            case OpCode.J3:
                self._jump(self.state.rI3)
            case OpCode.J4:
                self._jump(self.state.rI4)
            case OpCode.J5:
                self._jump(self.state.rI5)
            case OpCode.J6:
                self._jump(self.state.rI6)

            # S*
            case OpCode.SH:
                self._shift()

            # MOVE
            case OpCode.MOVE:
                self._move()

            # NOP
            case OpCode.NOP:
                pass

            # I/O
            case OpCode.IOC:
                # we assume the device is ready
                pass
            case OpCode.OUT:
                self._out()

            # CONV
            case OpCode.CONV:
                if self.field == 0:
                    self._num()
                elif self.field == 1:
                    self._char()

            # Unknown OpCode
            case _:
                raise ValueError(f"Unsupported opcode {self.opcode}")

    def _load(
        self, register: IndexRegister | WordRegister, negative: bool = False
    ) -> None:
        # load word at address
        m = self._get_address()
        word = self.state.memory[m]

        # select relevant fields
        sign, data = word.load_fields(*self.modification)

        if isinstance(register, IndexRegister):
            val = bytes_to_int(data)

            # LDi is invalid if setting any bytes other than the lowest two are set
            if val >= (1 << (BITS_IN_BYTE * 2)):
                raise ValueError(
                    "The LDi instruction is undefined if it would result in setting bytes 1, 2 or 3 to anything but zero."
                )
            else:
                data = data[-2:]

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
        word = self.state.memory[m]

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
        word = self.state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # add V to A
        a = int(self.state.rA)
        a += -v if negative else v

        # store back into A
        sign, result = int_to_bytes(a, padding=self.state.rA.BYTES)

        if len(result) == self.state.rA.BYTES + 1:
            self.state.overflow = True
            result = result[: self.state.rA.BYTES]

        self.state.rA.update(sign, *result)

    def _mul(self) -> None:
        # load the value in the instruction as an integer
        m = self._get_address()
        word = self.state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # multiple A by V
        a = int(self.state.rA)
        product = a * v

        # store back into A and X
        sign, result = int_to_bytes(
            product, padding=self.state.rA.BYTES + self.state.rX.BYTES
        )
        # X gets the low bytes
        self.state.rX.update(sign, *result[: self.state.rX.BYTES])
        # A gets the high bytes
        self.state.rA.update(sign, *result[self.state.rX.BYTES :])

    def _div(self) -> None:
        # load the value in the instruction as an integer
        m = self._get_address()
        word = self.state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(data, sign)

        # divide AX by V
        a = int(self.state.rA)
        x = int(self.state.rX)
        ax = (abs(a) << (BYTES_IN_WORD * BITS_IN_BYTE)) + abs(x)
        ax = -ax if a < 0 else ax
        quotient, remainder = divmod(ax, v)
        sign = sign != self.state.rA.sign

        # store quotient back into A
        _, result = int_to_bytes(quotient, padding=self.state.rA.BYTES)
        if len(result) > self.state.rA.BYTES:
            self.state.overflow = True
            result = result[: self.state.rA.BYTES]
        self.state.rA.update(sign, *result)

        # store remainder back into X
        _, result = int_to_bytes(remainder, padding=self.state.rX.BYTES)
        self.state.rX.update(sign, *result)

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
            self.state.overflow = True
            result = result[: register.BYTES]

        register.update(sign, *result)

    def _compare(self, register: IndexRegister | WordRegister) -> None:
        # an equal comparison always occurs when F is (0:0)
        if self.field == 0:
            self.state.comparison_indicator = ComparisonIndicator.EQUAL
            return

        # load word at address
        m = self._get_address()
        word = self.state.memory[m]

        # select relevant fields
        lsign, ldata = register.compare_fields(*self.modification)
        rsign, rdata = word.compare_fields(*self.modification)

        # compare the values
        left = bytes_to_int(ldata, lsign)
        right = bytes_to_int(rdata, rsign)

        if left < right:
            self.state.comparison_indicator = ComparisonIndicator.LESS
        elif left == right:
            self.state.comparison_indicator = ComparisonIndicator.EQUAL
        else:
            self.state.comparison_indicator = ComparisonIndicator.GREATER

    def _jump(self, register: IndexRegister | WordRegister | None) -> None:
        criteria_met = False

        # evaluate the jump criteria
        if self.opcode == OpCode.JMP:
            # JMP and JSP
            if self.field == 0 or self.field == 1:
                criteria_met = True
            # JOV - if the overflow toggle is on, it is turned off and a JMP occurs
            elif self.field == 2 and self.state.overflow:
                criteria_met = True
                self.state.overflow = False
            # JNOV - if the overflow toggle is off, a JMP occurs; otherwise it is turned off
            elif self.field == 3:
                if not self.state.overflow:
                    criteria_met = True
                else:
                    self.state.overflow = False
            # JL
            elif (
                self.field == 4
                and self.state.comparison_indicator == ComparisonIndicator.LESS
            ):
                criteria_met = True
            # JE
            elif (
                self.field == 5
                and self.state.comparison_indicator == ComparisonIndicator.EQUAL
            ):
                criteria_met = True
            # JG
            elif (
                self.field == 6
                and self.state.comparison_indicator == ComparisonIndicator.GREATER
            ):
                criteria_met = True
            # JGE
            elif (
                self.field == 7
                and self.state.comparison_indicator != ComparisonIndicator.LESS
            ):
                criteria_met = True
            # JNE
            elif (
                self.field == 8
                and self.state.comparison_indicator != ComparisonIndicator.EQUAL
            ):
                criteria_met = True
            # JLE
            elif (
                self.field == 9
                and self.state.comparison_indicator != ComparisonIndicator.GREATER
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
            hi, lo = divmod(self.state.program_counter, BYTE_UPPER_LIMIT)
            self.state.rJ.update(Byte(lo), Byte(hi))

        # perform the jump
        self.state.program_counter = self._get_address()

    def _shift(self) -> None:
        m = self._get_address()
        if m < 0:
            raise ValueError(f"Cannot shift by a negative amount ({m})")

        # reduce m by the amount of bytes in the register(s) to circular shift
        if self.field == 4 or self.field == 5:
            m %= self.state.rA.BYTES + self.state.rX.BYTES
        # shift by 0 is a NOP
        if m == 0:
            return
        bits_to_shift = BITS_IN_BYTE * m

        # SLA and SRA
        if self.field == 0 or self.field == 1:
            if m >= self.state.rA.BYTES:
                # all bytes were shifted out of A
                data = [Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)]
            else:
                a = abs(int(self.state.rA))
                new_value = (
                    a << bits_to_shift if self.field == 0 else a >> bits_to_shift
                )
                _, data = int_to_bytes(new_value)

            # set A
            self.state.rA.update(self.state.rA.sign, *data[: self.state.rA.BYTES])
        # SLAX and SRAX
        elif self.field == 2 or self.field == 3:
            if m >= self.state.rA.BYTES + self.state.rX.BYTES:
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
                ax = (
                    abs(int(self.state.rA)) << (BITS_IN_BYTE * self.state.rA.BYTES)
                ) + abs((int(self.state.rX)))
                new_value = (
                    ax << bits_to_shift if self.field == 2 else ax >> bits_to_shift
                )
                _, data = int_to_bytes(new_value)
                data = data[: self.state.rA.BYTES + self.state.rX.BYTES]

            # set A and X
            self.state.rX.update(self.state.rX.sign, *data[: self.state.rX.BYTES])
            self.state.rA.update(self.state.rA.sign, *data[self.state.rX.BYTES :])
        # SLC and SRC
        elif self.field == 4 or self.field == 5:
            rx, ra = self.state.rX, self.state.rA
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
            self.state.rX.update(self.state.rX.sign, *shifted[: self.state.rX.BYTES])
            self.state.rA.update(self.state.rA.sign, *shifted[self.state.rX.BYTES :])

    def _move(self) -> None:
        # if F = 0, nothing happens
        words = self.field
        if words == 0:
            return

        # if the src and dst are the same, nothing happens
        src = self._get_address()
        dst = int(self.state.rI1)
        if src == dst:
            return

        # if src < dst, start at the end so we don't overwrite later src indices
        indices = range(words - 1, -1, -1) if src < dst else range(words)

        # move the data
        for i in indices:
            self.state.memory[dst + i] = self.state.memory[src + i]

    def _out(self) -> None:
        match self.field:
            # line printer
            case 18:
                block_size = 24
                for i in range(block_size):
                    m = self._get_address()
                    word = self.state.memory[m + i]

                    for byte in (word.b1, word.b2, word.b3, word.b4, word.b5):
                        char = byte_to_char(byte)
                        print(char, end="")

                # newline
                print("")
            case _:
                raise NotImplementedError(
                    "Only the line print (field=18) is supported for I/O"
                )

    def _num(self) -> None:
        a = self.state.rA
        x = self.state.rX
        digits = [
            b.val % 10
            for b in (a.r1, a.r2, a.r3, a.r4, a.r5, x.r1, x.r2, x.r3, x.r4, x.r5)
        ]

        # build a decimal number from the base 10 digits
        num = 0
        for d in digits:
            num = (num * 10) + d

        # store back into A as bytes
        _, data = int_to_bytes(num)
        a.update(a.sign, *data[: a.BYTES])

    def _char(self) -> None:
        a = self.state.rA
        x = self.state.rX
        num = abs(int(a))
        # little endian base 10 byte representation of the value in A
        char_bytes: List[Byte] = []

        # convert int to char bytes
        while num:
            char = str(num % 10)
            char_bytes.append(char_to_byte(char))
            num //= 10

        # pad with "0" char to fill A and X
        while len(char_bytes) < a.BYTES + x.BYTES:
            char_bytes.append(char_to_byte("0"))

        # store back into A and X
        x.update(x.sign, *char_bytes[: x.BYTES])
        a.update(a.sign, *char_bytes[x.BYTES :])

    def _get_address(self) -> int:
        match self.index:
            case 0:
                return self.address
            case 1:
                return self.address + int(self.state.rI1)
            case 2:
                return self.address + int(self.state.rI2)
            case 3:
                return self.address + int(self.state.rI3)
            case 4:
                return self.address + int(self.state.rI4)
            case 5:
                return self.address + int(self.state.rI5)
            case 6:
                return self.address + int(self.state.rI6)
            case _:
                raise ValueError(f"Index must be value in range 0-6. Got {self.index}")
