from unittest import TestCase
from unittest.mock import mock_open, patch

from mix_simulator.byte import Byte
from mix_simulator.assembler import Assembler
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import Word


class TestAssembler(TestCase):
    def test_assemble_maximum(self) -> None:
        program = """X      EQU     1000
        MAXIMUM     STJ     EXIT
        INIT        ENT3    0,1
                    JMP     CHANGEM
        LOOP        CMPA    X,3
                    JGE     *+3
        CHANGEM     ENT2    0,3
                    LDA     X,3
                    DEC3    1
                    J3P     LOOP
        EXIT        HLT     0"""
        expected = [
            Word(False, Byte(0), Byte(9), Byte(0), Byte(2), Byte(32)),
            Word(False, Byte(0), Byte(0), Byte(1), Byte(2), Byte(51)),
            Word(False, Byte(0), Byte(5), Byte(0), Byte(0), Byte(39)),
            Word(False, Byte(15), Byte(40), Byte(3), Byte(5), Byte(56)),
            Word(False, Byte(0), Byte(7), Byte(0), Byte(7), Byte(39)),
            Word(False, Byte(0), Byte(0), Byte(3), Byte(2), Byte(50)),
            Word(False, Byte(15), Byte(40), Byte(3), Byte(5), Byte(8)),
            Word(False, Byte(0), Byte(1), Byte(0), Byte(1), Byte(51)),
            Word(False, Byte(0), Byte(3), Byte(0), Byte(2), Byte(43)),
            Word(False, Byte(0), Byte(0), Byte(0), Byte(2), Byte(5)),
        ]
        state = SimulatorState.initial_state()

        assembler = Assembler("maximum.mix", state)
        with patch("builtins.open", mock_open(read_data=program)):
            instructions = assembler.parse_program()
            assembler.write_program_to_memory(instructions)

        for i, word in enumerate(expected):
            self.assertEqual(word, state.memory[i])
