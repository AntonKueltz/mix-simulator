from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore

STATE = SimulatorState.initial_state()


class TestCompare(TestCase):
    def setUp(self) -> None:
        # set word 2000 to |+|0|0|1|2|3|
        STATE.memory[2000] = Word(False, Byte(0), Byte(0), Byte(1), Byte(2), Byte(3))

    @parameterized.expand(
        [
            # CMP |+|0|0|1|2|3| to |+|0|0|1|2|3|
            (
                False,
                (Byte(3), Byte(2), Byte(1), Byte(0), Byte(0)),
                5,
                ComparisonIndicator.EQUAL,
            ),
            # CMP |+|0|0|2|0|0| to |+|0|0|1|2|3|
            (
                False,
                (Byte(0), Byte(0), Byte(2), Byte(0), Byte(0)),
                5,
                ComparisonIndicator.GREATER,
            ),
            # CMP |+|0|0|1|0|3| to |+|0|0|1|2|3|
            (
                False,
                (Byte(3), Byte(0), Byte(1), Byte(0), Byte(0)),
                5,
                ComparisonIndicator.LESS,
            ),
            # CMP |-|0|0|1|2|3| to |+|0|0|1|2|3|
            (
                True,
                (Byte(3), Byte(2), Byte(1), Byte(0), Byte(0)),
                5,
                ComparisonIndicator.LESS,
            ),
            # CMP |-| to |+|
            (
                True,
                (Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
                0,
                ComparisonIndicator.EQUAL,
            ),
            # CMP |-|X|X|1|2|X| to |+|X|X|1|2|X|
            (
                True,
                (Byte(63), Byte(2), Byte(1), Byte(63), Byte(63)),
                3 * 8 + 4,
                ComparisonIndicator.EQUAL,
            ),
        ]
    )
    def test_execute_word_register(
        self,
        sign: bool,
        data: Tuple[Byte, ...],
        field: int,
        expected: ComparisonIndicator,
    ) -> None:
        # data is in little endian so that update function behaves correctly
        STATE.rA.update(sign, *data)
        instruction = Instruction(2000, 0, field, OpCode.CMPA, STATE)

        instruction.execute()

        self.assertEqual(expected, STATE.comparison_indicator)

    @parameterized.expand(
        [
            (OpCode.CMP1,),
            (OpCode.CMP2,),
            (OpCode.CMP3,),
            (OpCode.CMP4,),
            (OpCode.CMP5,),
            (OpCode.CMP6,),
        ]
    )
    def test_execute_index_register(self, opcode: OpCode) -> None:
        # CMPi 2000(2:3) => |+|X|0|0|i4|i5| < |+|X|0|1|X|X|
        instruction = Instruction(2000, 0, 2 * 8 + 3, opcode, STATE)
        instruction.execute()
        self.assertEqual(ComparisonIndicator.LESS, STATE.comparison_indicator)
