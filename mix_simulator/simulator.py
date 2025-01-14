from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass

from mix_simulator.byte import Byte, int_to_bytes
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.memory import Memory
from mix_simulator.register import IndexRegister, JumpRegister, WordRegister
from mix_simulator.word import BYTES_IN_WORD, Word


@dataclass
class SimulatorState:
    memory: Memory
    rA: WordRegister
    rX: WordRegister
    rI1: IndexRegister
    rI2: IndexRegister
    rI3: IndexRegister
    rI4: IndexRegister
    rI5: IndexRegister
    rI6: IndexRegister
    rJ: JumpRegister
    overflow: bool
    comparison_indicator: ComparisonIndicator
    program_counter: int

    @staticmethod
    def initial_state() -> SimulatorState:
        return SimulatorState(
            memory=Memory(),
            rA=WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            rX=WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
            rI1=IndexRegister(False, Byte(0), Byte(0)),
            rI2=IndexRegister(False, Byte(0), Byte(0)),
            rI3=IndexRegister(False, Byte(0), Byte(0)),
            rI4=IndexRegister(False, Byte(0), Byte(0)),
            rI5=IndexRegister(False, Byte(0), Byte(0)),
            rI6=IndexRegister(False, Byte(0), Byte(0)),
            rJ=JumpRegister(Byte(0), Byte(0)),
            overflow=False,
            comparison_indicator=ComparisonIndicator.LESS,
            program_counter=0,
        )


class Simulator:
    def __init__(self) -> None:
        self.state = SimulatorState.initial_state()

    def run(self, filename: str) -> None:
        # defer import to avoid circular import
        from mix_simulator.assembler import Assembler
        from mix_simulator.instruction import Instruction

        assembler = Assembler(filename, self.state)
        instructions = assembler.parse_program()
        assembler.write_program_to_memory(instructions)

        # HACK - write values to memory here to test against
        from random import randint

        values = [randint(-100, 100) for _ in range(20)]
        print(f"Finding the max of {values}")
        print(f"Expected: {max(values)}")

        for idx, n in enumerate(values):
            sign, data = int_to_bytes(n, padding=BYTES_IN_WORD)
            w = Word(sign, *reversed(data))
            self.state.memory[1000 + idx + 1] = w

        self.state.program_counter = 3000
        self.state.rI1.update(False, Byte(len(values)))
        # END HACK

        # load instruction from memory
        word = self.state.memory[self.state.program_counter]
        instruction = Instruction.from_word(word, self.state)
        self.state.program_counter += 1

        # run until we reach HALT instruction
        while not (instruction.opcode.value == 5 and instruction.field == 2):
            instruction.execute()
            word = self.state.memory[self.state.program_counter]
            instruction = Instruction.from_word(word, self.state)
            self.state.program_counter += 1

        # print the A register which is the default result store
        print(int(self.state.rA))


def execute() -> int:
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    Simulator().run(args.filename)
    return 0


if __name__ == "__main__":
    execute()
