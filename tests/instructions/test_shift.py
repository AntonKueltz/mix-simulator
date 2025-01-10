from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.simulator import SimulatorState

STATE = SimulatorState.initial_state()


class TestShift(TestCase):
    def test_execute_multiple(self) -> None:
        STATE.rA.update(False, Byte(5), Byte(4), Byte(3), Byte(2), Byte(1))
        STATE.rX.update(True, Byte(10), Byte(9), Byte(8), Byte(7), Byte(6))

        # SRAX 1
        instruction = Instruction(1, 0, 3, OpCode.SH, STATE)
        expected_a = WordRegister(False, Byte(0), Byte(1), Byte(2), Byte(3), Byte(4))
        expected_x = WordRegister(True, Byte(5), Byte(6), Byte(7), Byte(8), Byte(9))

        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

        # SLA 2
        instruction = Instruction(2, 0, 0, OpCode.SH, STATE)
        expected_a = WordRegister(False, Byte(2), Byte(3), Byte(4), Byte(0), Byte(0))
        expected_x = WordRegister(True, Byte(5), Byte(6), Byte(7), Byte(8), Byte(9))

        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

        # SRC 4
        instruction = Instruction(4, 0, 5, OpCode.SH, STATE)
        expected_a = WordRegister(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(2))
        expected_x = WordRegister(True, Byte(3), Byte(4), Byte(0), Byte(0), Byte(5))

        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

        # SRA 2
        instruction = Instruction(2, 0, 1, OpCode.SH, STATE)
        expected_a = WordRegister(False, Byte(0), Byte(0), Byte(6), Byte(7), Byte(8))
        expected_x = WordRegister(True, Byte(3), Byte(4), Byte(0), Byte(0), Byte(5))

        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

        # SLC 501
        instruction = Instruction(501, 0, 4, OpCode.SH, STATE)
        expected_a = WordRegister(False, Byte(0), Byte(6), Byte(7), Byte(8), Byte(3))
        expected_x = WordRegister(True, Byte(4), Byte(0), Byte(0), Byte(5), Byte(0))

        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)
