from __future__ import annotations
from typing import Tuple

from mix_simulator.byte import BITS_IN_BYTE, bytes_to_int, int_to_bytes
from mix_simulator.opcode import OpCode
from mix_simulator.register import ZERO_REGISTER, IndexRegister, WordRegister
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
                self._load("A")
            case OpCode.LDX:
                self._load("X")
            case OpCode.LD1:
                self._load("I1", is_index_register=True)
            case OpCode.LD2:
                self._load("I2", is_index_register=True)
            case OpCode.LD3:
                self._load("I3", is_index_register=True)
            case OpCode.LD4:
                self._load("I4", is_index_register=True)
            case OpCode.LD5:
                self._load("I5", is_index_register=True)
            case OpCode.LD6:
                self._load("I6", is_index_register=True)

            # LD*N
            case OpCode.LDAN:
                self._load("A", negative=True)
            case OpCode.LDXN:
                self._load("X", negative=True)
            case OpCode.LD1N:
                self._load("I1", is_index_register=True, negative=True)
            case OpCode.LD2N:
                self._load("I2", is_index_register=True, negative=True)
            case OpCode.LD3N:
                self._load("I3", is_index_register=True, negative=True)
            case OpCode.LD4N:
                self._load("I4", is_index_register=True, negative=True)
            case OpCode.LD5N:
                self._load("I5", is_index_register=True, negative=True)
            case OpCode.LD6N:
                self._load("I6", is_index_register=True, negative=True)

            # ST*
            case OpCode.STA:
                self._store("A")
            case OpCode.ST1:
                self._store("I1")
            case OpCode.ST2:
                self._store("I2")
            case OpCode.ST3:
                self._store("I3")
            case OpCode.ST4:
                self._store("I4")
            case OpCode.ST5:
                self._store("I5")
            case OpCode.ST6:
                self._store("I6")
            case OpCode.STJ:
                self._store("J")
            case OpCode.STZ:
                self._store("Z")

            # ENT* / ENN* / INC* / DEC*
            case OpCode.ATA:
                self._address_transfer("A")
            case OpCode.AT1:
                self._address_transfer("I1")
            case OpCode.AT2:
                self._address_transfer("I2")
            case OpCode.AT3:
                self._address_transfer("I3")
            case OpCode.AT4:
                self._address_transfer("I4")
            case OpCode.AT5:
                self._address_transfer("I5")
            case OpCode.AT6:
                self._address_transfer("I6")
            case OpCode.ATX:
                self._address_transfer("X")

            # Unknown OpCode
            case _:
                raise ValueError(f"Unsupported opcode {self.opcode}")

    def _load(
        self, register: str, is_index_register: bool = False, negative: bool = False
    ) -> None:
        # load word at address
        m = self._get_address()
        word = STATE.memory[m]

        # select relevant fields
        sign, data = word.load_fields(*self.modification)

        # LDi is invalid if setting any of the upper 3 bytes
        if is_index_register and len(data) > 2:
            raise ValueError(
                "The LDi instruction is undefined if it would result in setting bytes 1, 2 or 3 to anything but zero."
            )

        if negative:
            sign = not sign

        # set the value
        # flip the endianness of the data since the update function uses little endian
        little_endian_data = reversed(data)
        match register:
            case "A":
                STATE.rA.update(sign, *little_endian_data)
            case "X":
                STATE.rX.update(sign, *little_endian_data)
            case "I1":
                STATE.rI1.update(sign, *little_endian_data)
            case "I2":
                STATE.rI2.update(sign, *little_endian_data)
            case "I3":
                STATE.rI3.update(sign, *little_endian_data)
            case "I4":
                STATE.rI4.update(sign, *little_endian_data)
            case "I5":
                STATE.rI5.update(sign, *little_endian_data)
            case "I6":
                STATE.rI6.update(sign, *little_endian_data)
            case _:
                raise ValueError(f"Unknown register {register}")

    def _store(self, register: str) -> None:
        # get data from register
        match register:
            case "A":
                sign, data = STATE.rA.store_fields(*self.modification)
            case "X":
                sign, data = STATE.rX.store_fields(*self.modification)
            case "I1":
                sign, data = STATE.rI1.store_fields(*self.modification)
            case "I2":
                sign, data = STATE.rI2.store_fields(*self.modification)
            case "I3":
                sign, data = STATE.rI3.store_fields(*self.modification)
            case "I4":
                sign, data = STATE.rI4.store_fields(*self.modification)
            case "I5":
                sign, data = STATE.rI5.store_fields(*self.modification)
            case "I6":
                sign, data = STATE.rI6.store_fields(*self.modification)
            case "J":
                sign, data = STATE.rJ.store_fields(*self.modification)
            case "Z":
                sign, data = ZERO_REGISTER.store_fields(*self.modification)
            case _:
                raise ValueError(f"Unknown register {register}")

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
        sign, result = int_to_bytes(a, padding=BYTES_IN_WORD)

        if len(result) == BYTES_IN_WORD + 1:
            STATE.overflow = True
            result = result[:BYTES_IN_WORD]

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
        sign, result = int_to_bytes(product, padding=BYTES_IN_WORD * 2)
        # X gets the low bytes
        STATE.rX.update(sign, *result[:BYTES_IN_WORD])
        # A gets the high bytes
        STATE.rA.update(sign, *result[BYTES_IN_WORD:])

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
        _, result = int_to_bytes(quotient, padding=BYTES_IN_WORD)
        if len(result) > BYTES_IN_WORD:
            STATE.overflow = True
            result = result[:BYTES_IN_WORD]
        STATE.rA.update(sign, *result)

        # store remainder back into X
        _, result = int_to_bytes(remainder, padding=BYTES_IN_WORD)
        STATE.rX.update(sign, *result)

    def _address_transfer(self, register: str) -> None:
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

    def _enter(self, register: str, negative: bool = False) -> None:
        # TODO - does not support -0 currently

        # get the value of the address and interpret it as an integer
        m = self._get_address()
        sign, data = int_to_bytes(m)

        # flip the sign if negative
        if negative:
            sign = not sign

        # set the relevant register
        match register:
            case "A":
                STATE.rA.update(sign, *data)
            case "X":
                STATE.rX.update(sign, *data)
            case "I1":
                STATE.rI1.update(sign, *data)
            case "I2":
                STATE.rI2.update(sign, *data)
            case "I3":
                STATE.rI3.update(sign, *data)
            case "I4":
                STATE.rI4.update(sign, *data)
            case "I5":
                STATE.rI5.update(sign, *data)
            case "I6":
                STATE.rI6.update(sign, *data)
            case _:
                raise ValueError(f"Unknown register {register}")

    def _increment(self, register: str, negative: bool = False) -> None:
        # get the relevant register
        r: IndexRegister | WordRegister
        match register:
            case "A":
                r = STATE.rA
            case "X":
                r = STATE.rX
            case "I1":
                r = STATE.rI1
            case "I2":
                r = STATE.rI2
            case "I3":
                r = STATE.rI3
            case "I4":
                r = STATE.rI4
            case "I5":
                r = STATE.rI5
            case "I6":
                r = STATE.rI6
            case _:
                raise ValueError(f"Unknown register {register}")

        # compute increment / decrement
        m = self._get_address()
        i = int(r)
        i += -m if negative else m

        # store back into register
        sign, result = int_to_bytes(i, padding=BYTES_IN_WORD)

        if len(result) == BYTES_IN_WORD + 1:
            STATE.overflow = True
            result = result[:BYTES_IN_WORD]

        r.update(sign, *result)

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
