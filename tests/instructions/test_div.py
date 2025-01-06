from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.simulator import STATE
from mix_simulator.word import Word


class TestDiv(TestCase):
    def test_execute_DIV(self) -> None:
        STATE.memory[1000] = Word(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(3))
        STATE.rA.update(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        STATE.rX.update(False, Byte(17), Byte(0), Byte(0), Byte(0), Byte(0))
        expected_a = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(5))
        expected_x = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(2))

        instruction = Instruction(1000, 0, 5, OpCode.DIV)
        instruction.execute()

        self.assertEqual(expected_a, STATE.rA)
        self.assertEqual(expected_x, STATE.rX)
