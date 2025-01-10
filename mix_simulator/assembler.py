from dataclasses import dataclass
from re import match

from mix_simulator.byte import BYTE_UPPER_LIMIT, Byte
from mix_simulator.operator import Operator
from mix_simulator.word import Word


@dataclass
class AssemblyInstruction:
    loc: str | None
    opcode: int
    address: str
    index: int
    field: int


class Assembler:
    mix_file: str
    symbol_table: dict[str, int]

    def __init__(self, mix_file: str) -> None:
        self.mix_file = mix_file
        self.symbol_table = {}

    def parse_program(self) -> list[AssemblyInstruction]:
        """Read the assembly program, translate to machine code, and store in memory."""
        instructions: list[AssemblyInstruction] = []

        # read in the assembly instructions
        offset = 0  # number of directives that don't count towards memory address
        with open(self.mix_file, "r") as f:
            for i, line in enumerate(f):
                line = line.strip()

                if self._parse_directive(line):
                    offset += 1
                    continue

                instruction = self._parse_instruction(line)
                instructions.append(instruction)

                # write location and index in memory to the symbol table
                if instruction.loc is not None:
                    self.symbol_table[instruction.loc] = i - offset

        return instructions

    def write_program_to_memory(self, instructions: list[AssemblyInstruction]) -> None:
        from mix_simulator.simulator import (
            STATE,
        )  # defer import to avoid circular import

        for i, instruction in enumerate(instructions):
            address = self._parse_address(instruction.address, i)
            ahi, alo = divmod(address, BYTE_UPPER_LIMIT)
            sign = address < 0

            word = Word(
                sign,
                Byte(ahi),
                Byte(alo),
                Byte(instruction.index),
                Byte(instruction.field),
                Byte(instruction.opcode),
            )
            STATE.memory[i] = word

    def _parse_directive(self, line: str) -> bool:
        """Parse a directive to the assembler."""
        pattern = (
            r"^"  # start
            r"([a-zA-Z]+)"  # symbol
            r"\s+"  # space
            r"(EQU|ORIG)"  # directive
            r"\s+"  # space
            r"(\d+)"  # value
            r"$"
        )
        m = match(pattern, line)
        if not m:
            return False

        symbol, directive, value = m.groups()
        match directive:
            case "EQU":
                self.symbol_table[symbol.upper()] = int(value)
            case "ORIG":
                pass
            case _:
                raise ValueError(f"Invalid assembler directive {directive}")

        return True

    @staticmethod
    def _parse_instruction(line: str) -> AssemblyInstruction:
        """Parse a line of assembly into the relevant parts of a machine instruction."""
        pattern = (
            r"^"  # start
            r"([a-zA-Z]+\s+)?"  # optional location tag
            r"([a-zA-Z0-9]+\s+)"  # operator
            r"(\*?[\+\-]?[0-9]+|[a-zA-Z]+)"  # address
            r"(,[1-6])?"  # optional index
            r"(\(\d:\d\))?"  # optional field
            r"$"  # end
        )
        m = match(pattern, line)

        if m is None:
            raise ValueError(f"{line} is not a valid assembly instruction")

        loc, op, address, mindex, mfield = m.groups()

        if loc:
            loc = loc.strip().upper()

        operator = Operator(op.strip())
        code, default_field = operator.to_code_and_field()

        index = 0 if mindex is None else int(mindex.strip(","))
        field = default_field if mfield is None else int(mfield)

        return AssemblyInstruction(loc, code, address.upper(), index, field)

    def _parse_address(self, address: str, idx: int) -> int:
        try:
            # int address
            return int(address)
        except ValueError:
            # relative address * +/- d
            if address[0] == "*":
                return idx + int(address[1:])
            elif address in self.symbol_table:
                return self.symbol_table[address]
            else:
                raise ValueError(f"Address {address} is not in the symbol table.")
