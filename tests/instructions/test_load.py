from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import STATE
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore


class TestLoad(TestCase):
    def setUp(self) -> None:
        # set word 2000 to |-|80|3|4|5|
        STATE.memory[2000] = Word(True, Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))
        # set I1 to |+|0|2|
        STATE.rI1.update(False, Byte(2), Byte(0))

    @parameterized.expand(
        [
            # LDA 2000
            (Instruction(2000, 0, 5, OpCode.LDA), (True, 1, 16, 3, 5, 4)),
            # LDA 1998,1(3:5)
            (Instruction(1998, 1, 3 * 8 + 5, OpCode.LDA), (False, 0, 0, 3, 5, 4)),
        ]
    )
    def test_execute_word_register(
        self, test_input: Instruction, expected: Tuple[bool, int, int, int, int, int]
    ) -> None:
        esign, er1, er2, er3, er4, er5 = expected

        test_input.execute()

        self.assertEqual(esign, STATE.rA.sign)
        self.assertEqual(er1, STATE.rA.r1)
        self.assertEqual(er2, STATE.rA.r2)
        self.assertEqual(er3, STATE.rA.r3)
        self.assertEqual(er4, STATE.rA.r4)
        self.assertEqual(er5, STATE.rA.r5)

    def test_execute_index_register(self) -> None:
        # LD1 2000(1:2)
        instruction = Instruction(2000, 0, 8 + 2, OpCode.LD1)
        instruction.execute()

        self.assertEqual(False, STATE.rI1.sign)
        self.assertEqual(1, STATE.rI1.i4)
        self.assertEqual(16, STATE.rI1.i5)

    def test_execute_index_register_too_many_bytes(self) -> None:
        # LD1 2000
        instruction = Instruction(2000, 0, 5, OpCode.LD1)
        with self.assertRaises(ValueError):
            instruction.execute()  # try to load more than 2 bytes into an index register
