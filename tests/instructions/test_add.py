from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import STATE
from mix_simulator.register import WordRegister
from mix_simulator.word import Word


class TestAdd(TestCase):
    def test_execute(self) -> None:
        STATE.memory[1000] = Word(False, Byte(1), Byte(36), Byte(5), Byte(0), Byte(50))
        STATE.rA.update(False, Byte(22), Byte(2), Byte(1), Byte(18), Byte(19))
        expected = WordRegister(False, Byte(20), Byte(54), Byte(6), Byte(3), Byte(8))

        instruction = Instruction(1000, 0, 5, OpCode.ADD)
        instruction.execute()

        self.assertEqual(expected, STATE.rA)
