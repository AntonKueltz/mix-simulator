from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore


class TestInstruction(TestCase):
    @parameterized.expand(
        [
            # LDA 2000,2(0:3)
            (
                (False, (Byte(31), Byte(16), Byte(2), Byte(3), Byte(8))),
                (2000, 2, (0, 3), OpCode.LDA),
            ),
            # LDA 2000,2(1:3)
            (
                (False, (Byte(31), Byte(16), Byte(2), Byte(11), Byte(8))),
                (2000, 2, (1, 3), OpCode.LDA),
            ),
            # LDA 2000(1:3)
            (
                (False, (Byte(31), Byte(16), Byte(0), Byte(11), Byte(8))),
                (2000, 0, (1, 3), OpCode.LDA),
            ),
            # LDA 2000
            (
                (False, (Byte(31), Byte(16), Byte(0), Byte(5), Byte(8))),
                (2000, 0, (0, 5), OpCode.LDA),
            ),
            # LDA -2000,4
            (
                (True, (Byte(31), Byte(16), Byte(4), Byte(5), Byte(8))),
                (-2000, 4, (0, 5), OpCode.LDA),
            ),
        ]
    )
    def test_from_word_LDA(
        self,
        test_input: Tuple[bool, Tuple[Byte, Byte, Byte, Byte, Byte]],
        expected: Tuple[int, int, Tuple[int, int], OpCode],
    ) -> None:
        sign, data = test_input
        eaddress, eindex, emodification, eopcode = expected

        word = Word(sign, *data)
        instruction = Instruction.from_word(word)

        self.assertEqual(eaddress, instruction.address)
        self.assertEqual(eindex, instruction.index)
        self.assertEqual(emodification, instruction.modification)
        self.assertEqual(eopcode, instruction.opcode)

    def test_execute_LDA(self) -> None:
        from mix_simulator.simulator import state

        state.memory[2000] = Word(True, Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))

        # LDA 2000
        instruction = Instruction(2000, 0, (0, 5), OpCode.LDA)
        instruction.execute()

        self.assertEqual(True, state.rA.sign)
        self.assertEqual(1, state.rA.r1)
        self.assertEqual(16, state.rA.r2)
        self.assertEqual(3, state.rA.r3)
        self.assertEqual(5, state.rA.r4)
        self.assertEqual(4, state.rA.r5)

        # LDA 1998,2(3:5)
        state.rI1.update(False, Byte(2), Byte(0))
        instruction = Instruction(1998, 1, (3, 5), OpCode.LDA)
        instruction.execute()

        self.assertEqual(False, state.rA.sign)
        self.assertEqual(0, state.rA.r1)
        self.assertEqual(0, state.rA.r2)
        self.assertEqual(3, state.rA.r3)
        self.assertEqual(5, state.rA.r4)
        self.assertEqual(4, state.rA.r5)

    def test_execute_LD1(self) -> None:
        from mix_simulator.simulator import state

        state.memory[2000] = Word(True, Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))

        # LD1 2000(1:2)
        instruction = Instruction(2000, 0, (1, 2), OpCode.LD1)
        instruction.execute()

        self.assertEqual(80, int(state.rI1))

        # LD1 2000
        instruction = Instruction(2000, 0, (0, 5), OpCode.LD1)
        with self.assertRaises(ValueError):
            instruction.execute()  # try to load more than 2 bytes into an index register

    @parameterized.expand(
        [
            # STA 2000
            (
                Instruction(2000, 0, (0, 5), OpCode.STA),
                Word(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0)),
            ),
            # STA 2000(1:5)
            (
                Instruction(2000, 0, (1, 5), OpCode.STA),
                Word(True, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0)),
            ),
            # STA 2000(5:5)
            (
                Instruction(2000, 0, (5, 5), OpCode.STA),
                Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(0)),
            ),
            # STA 2000(2:2)
            (
                Instruction(2000, 0, (2, 2), OpCode.STA),
                Word(True, Byte(1), Byte(0), Byte(3), Byte(4), Byte(5)),
            ),
            # STA 2000(2:3)
            (
                Instruction(2000, 0, (2, 3), OpCode.STA),
                Word(True, Byte(1), Byte(9), Byte(0), Byte(4), Byte(5)),
            ),
            # STA 2000(0:1)
            (
                Instruction(2000, 0, (0, 1), OpCode.STA),
                Word(False, Byte(0), Byte(2), Byte(3), Byte(4), Byte(5)),
            ),
        ]
    )
    def test_execute_STA(self, test_input: Instruction, expected: Word) -> None:
        from mix_simulator.simulator import state

        state.rA.update(False, Byte(0), Byte(9), Byte(8), Byte(7), Byte(6))
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))

        test_input.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

    def test_execute_ST1(self) -> None:
        # TODO
        pass

    def test_execute_STJ(self) -> None:
        # TODO
        pass

    def test_execute_STZ(self) -> None:
        # TODO
        pass

    def test_execute_ADD(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(False, Byte(1), Byte(36), Byte(5), Byte(0), Byte(50))
        state.rA.update(False, Byte(22), Byte(2), Byte(1), Byte(18), Byte(19))
        expected = WordRegister(False, Byte(20), Byte(54), Byte(6), Byte(3), Byte(8))

        instruction = Instruction(1000, 0, (0, 5), OpCode.ADD)
        instruction.execute()

        self.assertEqual(expected, state.rA)

    def test_execute_SUB(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(True, Byte(31), Byte(16), Byte(2), Byte(22), Byte(0))
        state.rA.update(True, Byte(9), Byte(0), Byte(0), Byte(18), Byte(19))
        expected = WordRegister(False, Byte(11), Byte(62), Byte(2), Byte(21), Byte(55))

        instruction = Instruction(1000, 0, (0, 5), OpCode.SUB)
        instruction.execute()

        self.assertEqual(expected, state.rA)

    def test_execute_MUL(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(False, Byte(1), Byte(1), Byte(1), Byte(1), Byte(1))
        state.rA.update(False, Byte(1), Byte(1), Byte(1), Byte(1), Byte(1))
        expected_a = WordRegister(False, Byte(0), Byte(1), Byte(2), Byte(3), Byte(4))
        expected_x = WordRegister(False, Byte(5), Byte(4), Byte(3), Byte(2), Byte(1))

        instruction = Instruction(1000, 0, (0, 5), OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, state.rA)
        self.assertEqual(expected_x, state.rX)

    def test_execute_MUL_with_F(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(True, Byte(2), Byte(0), Byte(0), Byte(0), Byte(0))
        state.rA.update(True, Byte(48), Byte(1))
        expected_a = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        expected_x = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(3), Byte(32))

        instruction = Instruction(1000, 0, (1, 1), OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, state.rA)
        self.assertEqual(expected_x, state.rX)

    def test_execute_MUL_sparse(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(True, Byte(2), Byte(0), Byte(0), Byte(0), Byte(0))
        state.rA.update(True, Byte(4), Byte(48), Byte(1), Byte(0), Byte(50))
        expected_a = WordRegister(False, Byte(1), Byte(36), Byte(0), Byte(3), Byte(32))
        expected_x = WordRegister(False, Byte(8), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction = Instruction(1000, 0, (0, 5), OpCode.MUL)
        instruction.execute()

        self.assertEqual(expected_a, state.rA)
        self.assertEqual(expected_x, state.rX)

    def test_execute_DIV(self) -> None:
        from mix_simulator.simulator import state

        state.memory[1000] = Word(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(3))
        state.rA.update(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        state.rX.update(False, Byte(17), Byte(0), Byte(0), Byte(0), Byte(0))
        expected_a = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(5))
        expected_x = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(2))

        instruction = Instruction(1000, 0, (0, 5), OpCode.DIV)
        instruction.execute()

        self.assertEqual(expected_a, state.rA)
        self.assertEqual(expected_x, state.rX)
