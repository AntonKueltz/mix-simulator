from re import match
from unittest import TestCase

from mix_simulator.grammar import INSTRUCTION


class TestGrammar(TestCase):
    def test_parse_max_program(self) -> None:
        program = """X      EQU     1000
            ORIG    3000
MAXIMUM     STJ     EXIT
INIT        ENT3    0,1
            JMP     CHANGEM
LOOP        CMPA    X,3
            JGE     *+3
CHANGEM     ENT2    0,3
            LDA     X,3
            DEC3    1
            J3P     LOOP
EXIT        HALT    0"""
        expected = [
            # loc       op      address    index field
            ("X", "EQU", "1000", None, None),
            (None, "ORIG", "3000", None, None),
            ("MAXIMUM", "STJ", "EXIT", None, None),
            ("INIT", "ENT3", "0", "1", None),
            (None, "JMP", "CHANGEM", None, None),
            ("LOOP", "CMPA", "X", "3", None),
            (None, "JGE", "*+3", None, None),
            ("CHANGEM", "ENT2", "0", "3", None),
            (None, "LDA", "X", "3", None),
            (None, "DEC3", "1", None, None),
            (None, "J3P", "LOOP", None, None),
            ("EXIT", "HALT", "0", None, None),
        ]

        for i, line in enumerate(program.split("\n")):
            m = match(INSTRUCTION, line)
            if m is None:
                self.fail(f'"{line}" could not be parsed as an instruction')
            loc, op, addr, idx, f = m.groups()

            eloc, eop, eaddr, eidx, ef = expected[i]
            self.assertEqual(eloc, loc)
            self.assertEqual(eop, op)
            self.assertEqual(eaddr, addr)
            self.assertEqual(eidx, idx)
            self.assertEqual(ef, f)

    def test_parse_primes_program(self) -> None:
        program = """L       EQU     500
PRINTER EQU     18
PRIME   EQU     -1
BUF0    EQU     2000
BUF1    EQU     BUF0+25
        ORIG    3000"""
        expected = [
            # loc       op      address    index field
            ("L", "EQU", "500", None, None),
            ("PRINTER", "EQU", "18", None, None),
            ("PRIME", "EQU", "-1", None, None),
            ("BUF0", "EQU", "2000", None, None),
            ("BUF1", "EQU", "BUF0+25", None, None),
            (None, "ORIG", "3000", None, None),
        ]

        for i, line in enumerate(program.split("\n")):
            m = match(INSTRUCTION, line)
            if m is None:
                self.fail(f'"{line}" could not be parsed as an instruction')
            loc, op, addr, idx, f = m.groups()

            eloc, eop, eaddr, eidx, ef = expected[i]
            self.assertEqual(eloc, loc)
            self.assertEqual(eop, op)
            self.assertEqual(eaddr, addr)
            self.assertEqual(eidx, idx)
            self.assertEqual(ef, f)
