from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.simulator import STATE

from parameterized import parameterized  # type: ignore


class TestIncrement(TestCase):
    def setUp(self) -> None:
        # set I1 to |+|1|36| = 100
        STATE.rI1.update(False, Byte(36), Byte(1))
        # set A to |+|0|0|0|15|40| = 1000
        STATE.rA.update(False, Byte(40), Byte(15))

    @parameterized.expand(
        [
            # INCA 200
            (
                Instruction(200, 0, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(18), Byte(48)),
            ),
            # INCA -200
            (
                Instruction(-200, 0, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(12), Byte(32)),
            ),
            # INCA 200,1
            (
                Instruction(200, 1, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(20), Byte(20)),
            ),
            # DECA 200
            (
                Instruction(200, 0, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(12), Byte(32)),
            ),
            # DECA -200
            (
                Instruction(-200, 0, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(18), Byte(48)),
            ),
            # DECA 200,1
            (
                Instruction(200, 1, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(10), Byte(60)),
            ),
        ]
    )
    def test_execute(self, test_input: Instruction, expected: WordRegister) -> None:
        test_input.execute()
        self.assertEqual(expected, STATE.rA)

    def test_overflow(self) -> None:
        # set A to |+|63|63|63|63|63| = INT_MAX
        STATE.rA.update(False, Byte(63), Byte(63), Byte(63), Byte(63), Byte(63))
        instruction = Instruction(1, 0, 0, OpCode.ATA)
        expected = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction.execute()

        self.assertEqual(expected, STATE.rA)
        self.assertTrue(STATE.overflow)

        # clear overflow toggle
        STATE.overflow = False

        # set A to |-|63|63|63|63|63| = INT_MAX
        STATE.rA.update(True, Byte(63), Byte(63), Byte(63), Byte(63), Byte(63))
        instruction = Instruction(1, 0, 1, OpCode.ATA)
        expected = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction.execute()

        self.assertEqual(expected, STATE.rA)
        self.assertTrue(STATE.overflow)
