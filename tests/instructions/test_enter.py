from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
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
    def test_execute(self, test_input: Instruction, expected: WordRegister) -> None:
        test_input.execute()
        self.assertEqual(expected, STATE.rA)
