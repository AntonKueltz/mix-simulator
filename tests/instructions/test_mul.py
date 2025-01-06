from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import STATE
from mix_simulator.register import WordRegister
from mix_simulator.word import Word


class TestMul(TestCase):
    def test_execute(self) -> None:
        STATE.memory[1000] = Word(False, Byte(1), Byte(1), Byte(1), Byte(1), Byte(1))
        STATE.rA.update(False, Byte(1), Byte(1), Byte(1), Byte(1), Byte(1))
        expected_a = WordRegister(False, Byte(0), Byte(1), Byte(2), Byte(3), Byte(4))
        expected_x = WordRegister(False, Byte(5), Byte(4), Byte(3), Byte(2), Byte(1))

        instruction = Instruction(1000, 0, 5, OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

    def test_execute_with_field_selectors(self) -> None:
        STATE.memory[1000] = Word(True, Byte(2), Byte(0), Byte(0), Byte(0), Byte(0))
        STATE.rA.update(True, Byte(48), Byte(1))
        expected_a = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        expected_x = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(3), Byte(32))

        instruction = Instruction(1000, 0, 8 + 1, OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)

    def test_execute_sparse(self) -> None:
        STATE.memory[1000] = Word(True, Byte(2), Byte(0), Byte(0), Byte(0), Byte(0))
        STATE.rA.update(True, Byte(4), Byte(48), Byte(1), Byte(0), Byte(50))
        expected_a = WordRegister(False, Byte(1), Byte(36), Byte(0), Byte(3), Byte(32))
        expected_x = WordRegister(False, Byte(8), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction = Instruction(1000, 0, 5, OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)
