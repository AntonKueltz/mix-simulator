from random import randint
from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte, UPPER_LIMIT
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import IndexRegister
from mix_simulator.simulator import STATE
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore


class TestInstruction(TestCase):
    @parameterized.expand(
        [
            # LDA 2000,2(0:3)
            (
                (False, (Byte(31), Byte(16), Byte(2), Byte(3), Byte(8))),
                (2000, 2, (0, 3), OpCode.LDA),
            ),
            # LDA 2000,2(1:3)
            (
                (False, (Byte(31), Byte(16), Byte(2), Byte(11), Byte(8))),
                (2000, 2, (1, 3), OpCode.LDA),
            ),
            # LDA 2000(1:3)
            (
                (False, (Byte(31), Byte(16), Byte(0), Byte(11), Byte(8))),
                (2000, 0, (1, 3), OpCode.LDA),
            ),
            # LDA 2000
            (
                (False, (Byte(31), Byte(16), Byte(0), Byte(5), Byte(8))),
                (2000, 0, (0, 5), OpCode.LDA),
            ),
            # LDA -2000,4
            (
                (True, (Byte(31), Byte(16), Byte(4), Byte(5), Byte(8))),
                (-2000, 4, (0, 5), OpCode.LDA),
            ),
        ]
    )
    def test_from_word(
        self,
        test_input: Tuple[bool, Tuple[Byte, Byte, Byte, Byte, Byte]],
        expected: Tuple[int, int, Tuple[int, int], OpCode],
    ) -> None:
        sign, data = test_input
        eaddress, eindex, emodification, eopcode = expected

        word = Word(sign, *data)
        instruction = Instruction.from_word(word)

        self.assertEqual(eaddress, instruction.address)
        self.assertEqual(eindex, instruction.index)
        self.assertEqual(emodification, instruction.modification)
        self.assertEqual(eopcode, instruction.opcode)

    @parameterized.expand(
        [
            (Instruction(0, 1, 5, OpCode.NOP), STATE.rI1),
            (Instruction(0, 2, 5, OpCode.NOP), STATE.rI2),
            (Instruction(0, 3, 5, OpCode.NOP), STATE.rI3),
            (Instruction(0, 4, 5, OpCode.NOP), STATE.rI4),
            (Instruction(0, 5, 5, OpCode.NOP), STATE.rI5),
            (Instruction(0, 6, 5, OpCode.NOP), STATE.rI6),
        ]
    )
    def test_get_address(
        self, instruction: Instruction, register: IndexRegister
    ) -> None:
        expected = randint(0, STATE.memory.words)
        hi, lo = divmod(expected, UPPER_LIMIT)
        register.update(False, Byte(lo), Byte(hi))

        actual = instruction._get_address()

        self.assertEqual(expected, actual)
