from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import BYTE_UPPER_LIMIT, Byte, int_to_bytes
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import BYTES_IN_WORD, Word

from parameterized import parameterized  # type: ignore

STATE = SimulatorState.initial_state()


class TestMaximum(TestCase):
    @parameterized.expand(
        [
            ((1,), 1),
            ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 10),
            ((1, 3, 5, 7, 9, 2, 4, 6, 8), 9),
        ]
    )
    def test_program(self, test_input: Tuple[int], expected: int) -> None:
        # load elements into memory
        x = 100
        xhi, xlo = divmod(x, BYTE_UPPER_LIMIT)
        for i, n in enumerate(test_input):
            sign, data = int_to_bytes(n, padding=BYTES_IN_WORD)
            w = Word(sign, *reversed(data))
            STATE.memory[x + i + 1] = w

        # program description
        instruction_words = [
            Word(
                False, Byte(0), Byte(0), Byte(1), Byte(2), Byte(51)
            ),  #           INIT  ENT3 0,1
            Word(
                False, Byte(0), Byte(4), Byte(0), Byte(0), Byte(39)
            ),  #           JMP   CHANGEM
            Word(
                False, Byte(xhi), Byte(xlo), Byte(3), Byte(5), Byte(56)
            ),  # LOOP      CMPA  X,3
            Word(
                False, Byte(0), Byte(6), Byte(0), Byte(7), Byte(39)
            ),  #           GE    *+3
            Word(
                False, Byte(0), Byte(0), Byte(3), Byte(2), Byte(50)
            ),  # CHANGEM   ENT2  0,3
            Word(
                False, Byte(xhi), Byte(xlo), Byte(3), Byte(5), Byte(8)
            ),  #           LDA   X,3
            Word(
                False, Byte(0), Byte(1), Byte(0), Byte(1), Byte(51)
            ),  #           DEC3  1
            Word(
                False, Byte(0), Byte(2), Byte(0), Byte(2), Byte(43)
            ),  #           J3P   LOOP
            Word(False, Byte(0), Byte(0), Byte(0), Byte(2), Byte(5)),  #           HALT
        ]

        # load program into memory
        for i, instruction_word in enumerate(instruction_words):
            STATE.memory[i] = instruction_word

        # set initial state
        STATE.program_counter = 0
        STATE.rI1.update(False, Byte(len(test_input)))

        # run the program
        instruction = Instruction.from_word(STATE.memory[STATE.program_counter], STATE)
        STATE.program_counter += 1
        while not (instruction.opcode == OpCode(5) and instruction.field == 2):
            instruction.execute()
            instruction = Instruction.from_word(
                STATE.memory[STATE.program_counter], STATE
            )
            STATE.program_counter += 1

        # max value should be in A
        self.assertEqual(expected, int(STATE.rA))
