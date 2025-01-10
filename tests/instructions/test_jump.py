from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import JumpRegister
from mix_simulator.simulator import SimulatorState

from parameterized import parameterized  # type: ignore

STATE = SimulatorState.initial_state()


class TestJump(TestCase):
    def setUp(self) -> None:
        STATE.program_counter = 1000
        # set J to |+|1|36| = 100
        STATE.rJ.update(Byte(36), Byte(1))

    def test_execute_jmp(self) -> None:
        instruction = Instruction(2000, 0, 0, OpCode.JMP, STATE)
        expected = 2000
        j = JumpRegister(Byte(15), Byte(40))

        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)

    def test_execute_jsp(self) -> None:
        instruction = Instruction(2000, 0, 1, OpCode.JMP, STATE)
        expected = 2000
        j = JumpRegister(Byte(1), Byte(36))

        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)

    def test_execute_jov(self) -> None:
        instruction = Instruction(2000, 0, 2, OpCode.JMP, STATE)
        expected = 2000
        j = JumpRegister(Byte(15), Byte(40))

        STATE.overflow = True
        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)
        self.assertFalse(STATE.overflow)

    def test_execute_jnov_overflow_on(self) -> None:
        instruction = Instruction(2000, 0, 3, OpCode.JMP, STATE)
        expected = 1000
        j = JumpRegister(Byte(1), Byte(36))

        STATE.overflow = True
        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)
        self.assertFalse(STATE.overflow)

    def test_execute_jnov_overflow_off(self) -> None:
        instruction = Instruction(2000, 0, 3, OpCode.JMP, STATE)
        expected = 2000
        j = JumpRegister(Byte(15), Byte(40))

        STATE.overflow = False
        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)
        self.assertFalse(STATE.overflow)

    @parameterized.expand(
        [
            # JL 2000
            (
                Instruction(2000, 0, 4, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 4, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 4, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            # JE 2000
            (
                Instruction(2000, 0, 5, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 5, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 5, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            # JG 2000
            (
                Instruction(2000, 0, 6, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 6, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            (
                Instruction(2000, 0, 6, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            # JGE 2000
            (
                Instruction(2000, 0, 7, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 7, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 7, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            # JNE 2000
            (
                Instruction(2000, 0, 8, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 8, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 8, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
            # JLE 2000
            (
                Instruction(2000, 0, 9, OpCode.JMP, STATE),
                ComparisonIndicator.EQUAL,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 9, OpCode.JMP, STATE),
                ComparisonIndicator.LESS,
                2000,
                JumpRegister(Byte(15), Byte(40)),
            ),
            (
                Instruction(2000, 0, 9, OpCode.JMP, STATE),
                ComparisonIndicator.GREATER,
                1000,
                JumpRegister(Byte(1), Byte(36)),
            ),
        ]
    )
    def test_excute_jmp_comparison_op(
        self,
        instruction: Instruction,
        comparison_indicator: ComparisonIndicator,
        expected: int,
        j: JumpRegister,
    ) -> None:
        STATE.comparison_indicator = comparison_indicator

        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)

    @parameterized.expand(
        [
            # JAN
            (
                Instruction(2000, 0, 0, OpCode.JA, STATE),
                True,
                (Byte(1), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # JAZ
            (
                Instruction(2000, 0, 1, OpCode.JA, STATE),
                True,
                (Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # JAP
            (
                Instruction(2000, 0, 2, OpCode.JA, STATE),
                False,
                (Byte(1), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # JANN
            (
                Instruction(2000, 0, 3, OpCode.JA, STATE),
                True,
                (Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # JANZ
            (
                Instruction(2000, 0, 4, OpCode.JA, STATE),
                True,
                (Byte(1), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
            # JANP
            (
                Instruction(2000, 0, 5, OpCode.JA, STATE),
                False,
                (Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            ),
        ]
    )
    def test_execute_register(
        self, instruction: Instruction, sign: bool, data: Tuple[Byte]
    ) -> None:
        expected = 2000
        j = JumpRegister(Byte(15), Byte(40))

        STATE.rA.update(sign, *data)
        instruction.execute()

        self.assertEqual(expected, STATE.program_counter)
        self.assertEqual(j, STATE.rJ)
