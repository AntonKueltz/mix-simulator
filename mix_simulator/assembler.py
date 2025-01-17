from collections import defaultdict
from dataclasses import dataclass
from re import match, split

from mix_simulator.byte import BYTE_UPPER_LIMIT, Byte, int_to_bytes
from mix_simulator.character_code import char_to_byte
from mix_simulator.grammar import BINARY_OP, INSTRUCTION
from mix_simulator.operator import Operator
from mix_simulator.simulator import SimulatorState
from mix_simulator.word import BYTES_IN_WORD, Word


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
    here: dict[int, list[int]]
    state: SimulatorState
    word: int
    w_value_index: int

    def __init__(self, mix_file: str, state: SimulatorState) -> None:
        self.mix_file = mix_file
        self.symbol_table = {}
        self.here = defaultdict(list)
        self.state = state
        self.word = 0
        # store w values in ascending memory location, starting with the last cell
        self.w_value_index = state.memory.words - 1

    def parse_program(self) -> list[tuple[int, AssemblyInstruction]]:
        """Read the assembly program, translate to machine code, and store in memory."""
        instructions: list[tuple[int, AssemblyInstruction]] = []

        # read in the assembly instructions
        with open(self.mix_file, "r") as f:
            for line in f:
                # ignore comments (start with *) and empty lines
                if not line.strip() or line.startswith("*"):
                    continue

                parsed = self.process_line(line.rstrip())
                if parsed:
                    instructions.append(parsed)

        return instructions

    def process_line(self, line: str) -> tuple[int, AssemblyInstruction] | None:
        m = match(INSTRUCTION, line)
        if m is None:
            raise ValueError(f"{line} is not a valid MIXAL instruction.")

        loc, op, addr, idx, field = m.groups()
        if addr is None:
            addr = "0"

        # update the symbol table
        if loc is not None:
            # special "here" tag
            if match(r"^[0-9]H$", loc):
                i = int(loc[0])
                self.here[i].append(self.word)
            else:
                self.symbol_table[loc] = self.word

        # check for assembler directives
        match op:
            case "EQU":
                # have the location field resolve to the address value in the symbol table
                self.symbol_table[loc] = self._parse_address(addr, self.word)
                self.word += 1
                return None
            case "ORIG":
                # update where we are writing instructions in memory
                self.word = self._parse_address(addr, self.word)
                return None
            case "CON":
                # store the addr as a word in the memory location of the directive
                w_value = self._parse_address(addr, self.word)
                sign, bs = int_to_bytes(w_value, padding=BYTES_IN_WORD)
                self.state.memory[self.word] = Word(sign, *reversed(bs))
                self.word += 1
                return None
            case "ALF":
                # we use _ in place of space to make the language easier to parse
                chars = addr.replace("_", " ")
                bs = [char_to_byte(c) for c in chars]
                # store the chars as a word in the memory location of the directive
                self.state.memory[self.word] = Word(False, *bs)
                self.word += 1
                return None
            case "END":
                # tells the program counter where the first instruction is
                self.state.program_counter = self._parse_address(addr, self.word)
                return None
            case _:
                operator = Operator(op)
                code, dfield = operator.to_code_and_field()

                # set defaults
                idx = 0 if idx is None else int(idx)
                if field is None:
                    field = dfield
                else:
                    # remove parens before parsing field value
                    field = self._parse_address(field.strip("()"), self.word)

                # return instruction and location in memory
                result = (self.word, AssemblyInstruction(loc, code, addr, idx, field))
                self.word += 1
                return result

    def write_program_to_memory(
        self, instructions: list[tuple[int, AssemblyInstruction]]
    ) -> None:
        # sort the "here" locations so that we can do a linear search
        for locs in self.here.values():
            locs.sort()

        for i, instruction in instructions:
            # lookup a local symbol used as an address
            if match(r"^[0-9]F$", instruction.address) or match(
                r"^[0-9]B$", instruction.address
            ):
                address = self._resolve_here_ref(instruction.address, i)
            # resolve all other addresses
            else:
                address = self._parse_address(instruction.address, i)

            ahi, alo = divmod(abs(address), BYTE_UPPER_LIMIT)
            sign = address < 0

            word = Word(
                sign,
                Byte(ahi),
                Byte(alo),
                Byte(instruction.index),
                Byte(instruction.field),
                Byte(instruction.opcode),
            )
            self.state.memory[i] = word

    def _parse_address(self, address: str, i: int) -> int:
        # handle sign
        negative = False
        if address[0] == "-":
            negative = True
            address = address[1:]
        elif address[0] == "+":
            address = address[1:]

        result: int
        # reference to current instruction line
        if address == "*":
            result = i

        # number literal
        elif str.isdigit(address):
            result = int(address)

        # symbol reference
        elif str.isalnum(address):
            if address in self.symbol_table:
                result = self.symbol_table[address]
            else:
                raise ValueError(
                    f"{address} is was not found in the symbol table during parsing."
                )

        # w-value
        elif address.startswith("=") and address.endswith("="):
            address = address.strip("=")
            value = self._parse_address(address, i)

            # convert the expression to a word and store the word
            sign, bs = int_to_bytes(value, padding=BYTES_IN_WORD)
            word = Word(sign, *reversed(bs))
            self.state.memory[self.w_value_index] = word

            # returning the address where the word was stored
            result = self.w_value_index
            negative = False
            self.w_value_index -= 1

        # binary operator expression
        else:
            # disambiguate leftmost * as an address not an op
            if address[0] == "*":
                left = "*"
                _, op, right = split(rf"({BINARY_OP})", address[1:], maxsplit=1)
            else:
                left, op, right = split(rf"({BINARY_OP})", address, maxsplit=1)

            # parse recursively to support nested expressions
            lval = self._parse_address(left, i)
            rval = self._parse_address(right, i)

            match op:
                # ":" needs to be interpreted in a nonstandard way
                case ":":
                    result = 8 * lval + rval
                case _:
                    result = eval(f"{lval} {op} {rval}")

        # apply sign
        return -result if negative else result

    def _resolve_here_ref(self, address: str, cur: int) -> int:
        # This uses a O(n) linear search. O(log n) search is possible, but the lists
        # are not long enough for it to matter much and linear is more succinct.
        i = int(address[0])
        back = address[1] == "B"

        if back:
            for addr in reversed(self.here[i]):
                if addr < cur:
                    return addr
            else:
                raise ValueError(
                    f"{address} used for word at index {cur}, but there are no relevant local symbols before this address."
                )
        else:
            for addr in self.here[i]:
                if addr > cur:
                    return addr
            else:
                raise ValueError(
                    f"{address} used for word at index {cur}, but there are no relevant local symbols after this address."
                )
