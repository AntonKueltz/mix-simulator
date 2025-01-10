from random import choice, randint
from typing import List, Tuple
from unittest import TestCase

from mix_simulator.byte import BYTE_UPPER_LIMIT, Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import BYTES_IN_WORD, Word

from parameterized import parameterized  # type: ignore

STATE = SimulatorState.initial_state()


class TestMove(TestCase):
    def _random_words(self, count: int) -> List[Word]:
        words = []
        for _ in range(count):
            sign = choice([False, True])
            data = [
                Byte(randint(0, BYTE_UPPER_LIMIT - 1)) for _ in range(BYTES_IN_WORD)
            ]
            words.append(Word(sign, *data))
        return words

    @parameterized.expand(
        [
            # MOVE 1000 (to 999)
            (Instruction(1000, 0, 3, OpCode.MOVE, STATE), (Byte(39), Byte(15))),
            # MOVE 1000 (to 999)
            (Instruction(1, 1, 3, OpCode.MOVE, STATE), (Byte(39), Byte(15))),
            # MOVE 1000 (to 1001)
            (Instruction(1000, 0, 3, OpCode.MOVE, STATE), (Byte(41), Byte(15))),
            # MOVE 1000 (to 1001)
            (Instruction(-1, 1, 3, OpCode.MOVE, STATE), (Byte(41), Byte(15))),
            # MOVE 1000 (to 1000)
            (Instruction(1000, 0, 3, OpCode.MOVE, STATE), (Byte(40), Byte(15))),
            # MOVE 1000 (to 1000)
            (Instruction(0, 1, 3, OpCode.MOVE, STATE), (Byte(40), Byte(15))),
            # MOVE 1000 (to 2000)
            (Instruction(1000, 0, 3, OpCode.MOVE, STATE), (Byte(16), Byte(31))),
            # MOVE 1000 (to 100)
            (Instruction(1000, 0, 3, OpCode.MOVE, STATE), (Byte(36), Byte(1))),
        ]
    )
    def test_execute(self, instruction: Instruction, i1: Tuple[Byte, Byte]) -> None:
        STATE.rI1.update(False, *i1)
        words = self._random_words(instruction.field)

        src = instruction._get_address()
        for i, word in enumerate(words):
            STATE.memory[src + i] = word

        instruction.execute()

        dst = int(STATE.rI1)
        for i, word in enumerate(words):
            self.assertEqual(words[i], STATE.memory[dst + i])

    def test_execute_move_zero_words(self) -> None:
        # set I1 to |+|1|36| = 100
        STATE.rI1.update(False, Byte(36), Byte(1))
        sdata, ddata = self._random_words(2)
        instruction = Instruction(1000, 0, 0, OpCode.MOVE, STATE)

        src = instruction._get_address()
        dst = int(STATE.rI1)
        STATE.memory[src] = sdata
        STATE.memory[dst] = ddata
        instruction.execute()

        self.assertEqual(sdata, STATE.memory[src])
        self.assertEqual(ddata, STATE.memory[dst])
