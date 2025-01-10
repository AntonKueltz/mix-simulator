from random import randint
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import IndexRegister
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore

STATE = SimulatorState.initial_state()


class TestStore(TestCase):
    def setUp(self) -> None:
        # set A to |+|6|7|8|9|0|
        STATE.rA.update(False, Byte(0), Byte(9), Byte(8), Byte(7), Byte(6))
        # set word 2000 to |-|1|2|3|4|5|
        STATE.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        # set I1 to |+|0|2|
        STATE.rI1.update(False, Byte(2), Byte(0))
        # set J to |10|11|
        STATE.rJ.update(Byte(11), Byte(10))

    @parameterized.expand(
        [
            # STA 2000
            (
                Instruction(2000, 0, 5, OpCode.STA, STATE),
                Word(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0)),
            ),
            # STA 1998,1
            (
                Instruction(1998, 1, 5, OpCode.STA, STATE),
                Word(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0)),
            ),
            # STA 2000(1:5)
            (
                Instruction(2000, 0, 8 + 5, OpCode.STA, STATE),
                Word(True, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0)),
            ),
            # STA 2000(5:5)
            (
                Instruction(2000, 0, 5 * 8 + 5, OpCode.STA, STATE),
                Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(0)),
            ),
            # STA 2000(2:2)
            (
                Instruction(2000, 0, 2 * 8 + 2, OpCode.STA, STATE),
                Word(True, Byte(1), Byte(0), Byte(3), Byte(4), Byte(5)),
            ),
            # STA 2000(2:3)
            (
                Instruction(2000, 0, 2 * 8 + 3, OpCode.STA, STATE),
                Word(True, Byte(1), Byte(9), Byte(0), Byte(4), Byte(5)),
            ),
            # STA 2000(0:1)
            (
                Instruction(2000, 0, 1, OpCode.STA, STATE),
                Word(False, Byte(0), Byte(2), Byte(3), Byte(4), Byte(5)),
            ),
        ]
    )
    def test_execute_word_register(
        self, test_input: Instruction, expected: Word
    ) -> None:
        test_input.execute()
        actual = STATE.memory[2000]

        self.assertEqual(expected, actual)

    @parameterized.expand(
        [
            (OpCode.ST1, STATE.rI1),
            (OpCode.ST2, STATE.rI2),
            (OpCode.ST3, STATE.rI3),
            (OpCode.ST4, STATE.rI4),
            (OpCode.ST5, STATE.rI5),
            (OpCode.ST6, STATE.rI6),
        ]
    )
    def test_execute_index_register(
        self, opcode: OpCode, register: IndexRegister
    ) -> None:
        instruction = Instruction(2000, 0, 3 * 8 + 5, opcode, STATE)
        a, b = randint(0, 63), randint(0, 63)
        register.update(False, Byte(b), Byte(a))
        expected = Word(True, Byte(1), Byte(2), Byte(0), Byte(a), Byte(b))

        instruction.execute()
        actual = STATE.memory[2000]

        self.assertEqual(expected, actual)

    @parameterized.expand(
        [
            # STZ 2000
            (
                Instruction(2000, 0, 2, OpCode.STJ, STATE),
                Word(False, Byte(10), Byte(11), Byte(3), Byte(4), Byte(5)),
            ),
            # STZ 2000(1:2)
            (
                Instruction(2000, 0, 8 + 2, OpCode.STJ, STATE),
                Word(True, Byte(10), Byte(11), Byte(3), Byte(4), Byte(5)),
            ),
            # STZ 1998,1(2:2)
            (
                Instruction(1998, 1, 2 * 8 + 2, OpCode.STJ, STATE),
                Word(True, Byte(1), Byte(11), Byte(3), Byte(4), Byte(5)),
            ),
        ]
    )
    def test_execute_jump_register(
        self, test_input: Instruction, expected: Word
    ) -> None:
        test_input.execute()
        actual = STATE.memory[2000]

        self.assertEqual(expected, actual)

    @parameterized.expand(
        [
            # STZ 2000
            (
                Instruction(2000, 0, 5, OpCode.STZ, STATE),
                Word(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # STZ 2000(0:2)
            (
                Instruction(2000, 0, 2, OpCode.STZ, STATE),
                Word(False, Byte(0), Byte(0), Byte(3), Byte(4), Byte(5)),
            ),
            # STZ 1998,1(3:5)
            (
                Instruction(1998, 1, 3 * 8 + 5, OpCode.STZ, STATE),
                Word(True, Byte(1), Byte(2), Byte(0), Byte(0), Byte(0)),
            ),
        ]
    )
    def test_execute_zero(self, test_input: Instruction, expected: Word) -> None:
        test_input.execute()
        actual = STATE.memory[2000]

        self.assertEqual(expected, actual)
