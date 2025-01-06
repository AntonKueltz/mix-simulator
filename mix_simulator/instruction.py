from __future__ import annotations
from typing import Tuple

from mix_simulator.byte import BITS_IN_BYTE, Byte, bytes_to_int, int_to_bytes
from mix_simulator.opcode import OpCode
from mix_simulator.word import BYTES_IN_WORD, Word


class Instruction:
    """An instruction that can be executed by the simulator."""

    address: int
    index: int
    modification: Tuple[int, int]
    opcode: OpCode

    def __init__(
        self, address: int, index: int, modification: Tuple[int, int], opcode: OpCode
    ) -> None:
        self.address = address
        self.index = index
        self.modification = modification
        self.opcode = opcode

    @staticmethod
    def from_word(word: Word) -> Instruction:
        address = bytes_to_int((word.b1, word.b2))
        if word.sign:
            address *= -1

        index = word.b3.val
        modification = divmod(word.b4.val, 8)
        opcode = OpCode(word.b5.val)

        return Instruction(address, index, modification, opcode)

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
                self._store_j()
            case OpCode.STZ:
                self._store_zero()

            # Unknown OpCode
            case _:
                raise ValueError(f"Unsupported opcode {self.opcode}")

    def _load(
        self, register: str, is_index_register: bool = False, negative: bool = False
    ) -> None:
        from mix_simulator.simulator import state

        # load word at address
        m = self._get_address()
        word = state.memory[m]

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
        match register:
            case "A":
                state.rA.update(sign, *reversed(data))
            case "X":
                state.rX.update(sign, *reversed(data))
            case "I1":
                state.rI1.update(sign, *reversed(data))
            case "I2":
                state.rI2.update(sign, *reversed(data))
            case "I3":
                state.rI3.update(sign, *reversed(data))
            case "I4":
                state.rI4.update(sign, *reversed(data))
            case "I5":
                state.rI5.update(sign, *reversed(data))
            case "I6":
                state.rI6.update(sign, *reversed(data))
            case _:
                raise ValueError(f"Unknown register {register}")

    def _store(self, register: str) -> None:
        from mix_simulator.simulator import state

        # get data from register
        match register:
            case "A":
                sign, data = state.rA.store_fields(*self.modification)
            case _:
                raise ValueError(f"Unknown register {register}")

        # get the word to update
        m = self._get_address()
        word = state.memory[m]

        # store the data in the word
        if sign is not None:
            word.sign = sign

        # look at the range of l:r that we need to insert in
        # l must start at 1, since 0 is the sign index
        lo, hi = self.modification
        indices = range(max(lo, 1), hi + 1)
        for i, d in zip(indices, data):
            word.update(i, d)

    def _store_j(self) -> None:
        from mix_simulator.simulator import state

        m = self._get_address()
        word = state.memory[m]

        # TODO - this only supports F = (0:2)
        word.sign = False
        word.update(1, state.rJ.i4)
        word.update(2, state.rJ.i5)

    def _store_zero(self) -> None:
        from mix_simulator.simulator import state

        m = self._get_address()
        word = state.memory[m]

        word.sign = False
        for i in range(1, 6):
            word.update(i, Byte(0))

    def _add(self, negative: bool = False) -> None:
        from mix_simulator.simulator import state

        # load the value in the instruction as an integer
        m = self._get_address()
        word = state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(reversed(data), sign)

        # add V to A
        a = int(state.rA)
        a += -v if negative else v
        sign = state.rA.sign if a == 0 else a < 0

        # store back into A
        result = int_to_bytes(a, padding=BYTES_IN_WORD)

        if len(result) == BYTES_IN_WORD + 1:
            state.overflow = True
            result = result[:BYTES_IN_WORD]
        elif len(result) > BYTES_IN_WORD:
            raise ArithmeticError(
                f"Adding {a=} and {v=} resulted in a {len(result)} word number"
            )

        state.rA.update(sign, *result)

    def _mul(self) -> None:
        from mix_simulator.simulator import state

        # load the value in the instruction as an integer
        m = self._get_address()
        word = state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(reversed(data), sign)

        # multiple A by V
        a = int(state.rA)
        product = a * v
        sign = sign != state.rA.sign

        # store back into A and X
        result = int_to_bytes(product, padding=BYTES_IN_WORD * 2)
        # X gets the low bytes
        state.rX.update(sign, *result[:BYTES_IN_WORD])
        # A gets the high bytes
        state.rA.update(sign, *result[BYTES_IN_WORD:])

    def _div(self) -> None:
        from mix_simulator.simulator import state

        # load the value in the instruction as an integer
        m = self._get_address()
        word = state.memory[m]
        sign, data = word.load_fields(*self.modification)
        v = bytes_to_int(reversed(data), sign)

        # divide AX by V
        a = int(state.rA)
        x = int(state.rX)
        ax = (abs(a) << (BYTES_IN_WORD * BITS_IN_BYTE)) + abs(x)
        ax = -ax if a < 0 else ax
        quotient, remainder = divmod(ax, v)
        sign = sign != state.rA.sign

        # store quotient back into A
        result = int_to_bytes(quotient, padding=BYTES_IN_WORD)
        if len(result) > BYTES_IN_WORD:
            state.overflow = True
            result = result[:BYTES_IN_WORD]
        state.rA.update(sign, *result)

        # store remainder back into X
        result = int_to_bytes(remainder, padding=BYTES_IN_WORD)
        state.rX.update(sign, *result)

    def _get_address(self) -> int:
        from mix_simulator.simulator import state

        match self.index:
            case 0:
                return self.address
            case 1:
                return self.address + int(state.rI1)
            case 2:
                return self.address + int(state.rI2)
            case 3:
                return self.address + int(state.rI3)
            case 4:
                return self.address + int(state.rI4)
            case 5:
                return self.address + int(state.rI5)
            case 6:
                return self.address + int(state.rI6)
            case _:
                raise ValueError(f"Index must be value in range 0-6. Got {self.index}")
