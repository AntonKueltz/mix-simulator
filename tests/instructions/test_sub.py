from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import STATE
from mix_simulator.register import WordRegister
from mix_simulator.word import Word


class TestSub(TestCase):
    def test_execute(self) -> None:
        STATE.memory[1000] = Word(True, Byte(31), Byte(16), Byte(2), Byte(22), Byte(0))
        STATE.rA.update(True, Byte(9), Byte(0), Byte(0), Byte(18), Byte(19))
        expected = WordRegister(False, Byte(11), Byte(62), Byte(2), Byte(21), Byte(55))

        instruction = Instruction(1000, 0, (0, 5), OpCode.SUB)
        instruction.execute()

        self.assertEqual(expected, STATE.rA)
