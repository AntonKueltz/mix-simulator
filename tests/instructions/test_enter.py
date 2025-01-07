from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import IndexRegister, WordRegister
from mix_simulator.simulator import STATE

from parameterized import parameterized  # type: ignore


class TestEnter(TestCase):
    def setUp(self) -> None:
        # set I1 to |+|15|40| = 1000
        STATE.rI1.update(False, Byte(40), Byte(15))

    @parameterized.expand(
        [
            # ENTA 2000
            (
                Instruction(2000, 0, 2, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(31), Byte(16)),
            ),
            # ENTA -2000
            (
                Instruction(-2000, 0, 2, OpCode.ATA),
                WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(31), Byte(16)),
            ),
            # ENNA 2000
            (
                Instruction(2000, 0, 3, OpCode.ATA),
                WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(31), Byte(16)),
            ),
            # ENNA -2000
            (
                Instruction(-2000, 0, 3, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(31), Byte(16)),
            ),
            # ENTA 2000,1
            (
                Instruction(2000, 1, 2, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(46), Byte(56)),
            ),
            # ENTA -2000,1
            (
                Instruction(-2000, 1, 2, OpCode.ATA),
                WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(15), Byte(40)),
            ),
            # ENNA 2000,1
            (
                Instruction(2000, 1, 3, OpCode.ATA),
                WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(46), Byte(56)),
            ),
            # ENNA -2000,1
            (
                Instruction(-2000, 1, 3, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(15), Byte(40)),
            ),
        ]
    )
    def test_execute_word_register(
        self, test_input: Instruction, expected: WordRegister
    ) -> None:
        test_input.execute()
        self.assertEqual(expected, STATE.rA)

    @parameterized.expand(
        [
            (OpCode.AT1, STATE.rI1, 2, False),
            (OpCode.AT2, STATE.rI2, 2, False),
            (OpCode.AT3, STATE.rI3, 2, False),
            (OpCode.AT4, STATE.rI4, 2, False),
            (OpCode.AT5, STATE.rI5, 2, False),
            (OpCode.AT6, STATE.rI6, 2, False),
            (OpCode.AT1, STATE.rI1, 3, True),
            (OpCode.AT2, STATE.rI2, 3, True),
            (OpCode.AT3, STATE.rI3, 3, True),
            (OpCode.AT4, STATE.rI4, 3, True),
            (OpCode.AT5, STATE.rI5, 3, True),
            (OpCode.AT6, STATE.rI6, 3, True),
        ]
    )
    def test_execute_enter_index_register(
        self, opcode: OpCode, register: IndexRegister, variant: int, sign: bool
    ) -> None:
        instruction = Instruction(100, 1, variant, opcode)
        expected = IndexRegister(sign, Byte(17), Byte(12))

        instruction.execute()

        self.assertEqual(expected, register)
