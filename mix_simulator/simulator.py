from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass

from mix_simulator.byte import Byte
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.memory import Memory
from mix_simulator.register import IndexRegister, JumpRegister, WordRegister


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


def execute() -> int:
    parser = ArgumentParser()
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    Simulator().run(args.filename)
    return 0


if __name__ == "__main__":
    execute()
