from unittest import TestCase

from mix_simulator.byte import Byte, int_to_bytes
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import WordRegister
from mix_simulator.word import Word


class TestInstruction(TestCase):
    def test_from_word_LDA(self) -> None:
        # LDA 2000,2(0:3)
        [b1, b2] = int_to_bytes(2000)
        b3 = Byte(2)
        b4 = Byte(3)
        b5 = Byte(8)
        word = Word(False, b1, b2, b3, b4, b5)

        instruction = Instruction.from_word(word)

        self.assertEqual(OpCode.LDA, instruction.opcode)
        self.assertEqual(2000, instruction.address)
        self.assertEqual(2, instruction.index)
        self.assertEqual((0, 3), instruction.modification)

        # LDA 2000,2(1:3)
        b4 = Byte(11)
        word = Word(False, b1, b2, b3, b4, b5)

        instruction = Instruction.from_word(word)

        self.assertEqual(OpCode.LDA, instruction.opcode)
        self.assertEqual(2000, instruction.address)
        self.assertEqual(2, instruction.index)
        self.assertEqual((1, 3), instruction.modification)

        # LDA 2000(1:3)
        b3 = Byte(0)
        word = Word(False, b1, b2, b3, b4, b5)

        instruction = Instruction.from_word(word)

        self.assertEqual(OpCode.LDA, instruction.opcode)
        self.assertEqual(2000, instruction.address)
        self.assertEqual(0, instruction.index)
        self.assertEqual((1, 3), instruction.modification)

        # LDA 2000
        b4 = Byte(5)
        word = Word(False, b1, b2, b3, b4, b5)

        instruction = Instruction.from_word(word)

        self.assertEqual(OpCode.LDA, instruction.opcode)
        self.assertEqual(2000, instruction.address)
        self.assertEqual(0, instruction.index)
        self.assertEqual((0, 5), instruction.modification)

        # LDA -2000,4
        b3 = Byte(4)
        word = Word(True, b1, b2, b3, b4, b5)

        instruction = Instruction.from_word(word)

        self.assertEqual(OpCode.LDA, instruction.opcode)
        self.assertEqual(-2000, instruction.address)
        self.assertEqual(4, instruction.index)
        self.assertEqual((0, 5), instruction.modification)

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
        instruction = Instruction(1998, 2, (3, 5), OpCode.LDA)
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

    def test_execute_STA(self) -> None:
        from mix_simulator.simulator import state

        state.rA.update(False, Byte(0), Byte(9), Byte(8), Byte(7), Byte(6))

        # STA 2000
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (0, 5), OpCode.STA)
        expected = Word(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0))

        instruction.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

        # STA 2000(1:5)
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (1, 5), OpCode.STA)
        expected = Word(True, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0))

        instruction.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

        # STA 2000(5:5)
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (5, 5), OpCode.STA)
        expected = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(0))

        instruction.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

        # STA 2000(2:2)
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (2, 2), OpCode.STA)
        expected = Word(True, Byte(1), Byte(0), Byte(3), Byte(4), Byte(5))

        instruction.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

        # STA 2000(2:3)
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (2, 3), OpCode.STA)
        expected = Word(True, Byte(1), Byte(9), Byte(0), Byte(4), Byte(5))

        instruction.execute()
        actual = state.memory[2000]

        self.assertEqual(expected, actual)

        # STA 2000(0:1)
        state.memory[2000] = Word(True, Byte(1), Byte(2), Byte(3), Byte(4), Byte(5))
        instruction = Instruction(2000, 0, (0, 1), OpCode.STA)
        expected = Word(False, Byte(0), Byte(2), Byte(3), Byte(4), Byte(5))

        instruction.execute()
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
