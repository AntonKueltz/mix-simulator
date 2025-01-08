from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.simulator import STATE


class TestConversion(TestCase):
    def test_execute_multiple(self) -> None:
        # set A to |-|00|00|31|32|39|
        STATE.rA.update(True, Byte(39), Byte(32), Byte(31), Byte(0), Byte(0))
        # set X to |+|37|57|47|30|30|
        STATE.rX.update(False, Byte(30), Byte(30), Byte(47), Byte(57), Byte(37))

        # NUM 0
        instruction = Instruction(0, 0, 0, OpCode.CONV)
        instruction.execute()
        expected = -12977700
        self.assertEqual(expected, int(STATE.rA))

        # INCA 1
        instruction = Instruction(1, 0, 0, OpCode.ATA)
        instruction.execute()
        expected = -12977699
        self.assertEqual(expected, int(STATE.rA))

        # CHAR 0
        instruction = Instruction(0, 0, 1, OpCode.CONV)
        instruction.execute()
        expected_a = WordRegister(
            True, Byte(30), Byte(30), Byte(31), Byte(32), Byte(39)
        )
        expected_x = WordRegister(
            False, Byte(37), Byte(37), Byte(36), Byte(39), Byte(39)
        )
        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)
