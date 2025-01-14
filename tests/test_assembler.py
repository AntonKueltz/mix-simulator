from unittest import TestCase
from unittest.mock import mock_open, patch

from mix_simulator.byte import Byte
from mix_simulator.assembler import Assembler
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore


class TestAssembler(TestCase):
    @parameterized.expand(
        [
            ("500", {}, 0, 500),
            ("-1", {}, 0, -1),
            ("BUF0+25", {"BUF0": 2000}, 0, 2025),
            ("PRIME+L", {"PRIME": -1, "L": 500}, 0, 499),
            ("*+3", {}, 3000, 3003),
            ("***", {}, -30, 900),
        ]
    )
    def test_parse_address(
        self, addr: str, symtab: dict[str, int], word: int, expected: int
    ) -> None:
        assembler = Assembler("", SimulatorState.initial_state())
        assembler.symbol_table = symtab

        actual = assembler._parse_address(addr, word)

        self.assertEqual(expected, actual)

    def test_assemble_maximum(self) -> None:
        program = """X      EQU     1000
            ORIG    0
MAXIMUM     STJ     EXIT
INIT        ENT3    0,1
            JMP     CHANGEM
LOOP        CMPA    X,3
            JGE     *+3
CHANGEM     ENT2    0,3
            LDA     X,3
            DEC3    1
            J3P     LOOP
EXIT        HLT"""
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
