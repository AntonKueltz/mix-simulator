from dataclasses import dataclass

from mix_simulator.byte import Byte
from mix_simulator.comparison_indicator import ComparisonIndicator
from mix_simulator.memory import Memory
from mix_simulator.register import IndexRegister, WordRegister


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
    rJ: IndexRegister
    overflow: bool
    comparison_indicator: ComparisonIndicator
    # labels: Dict[str: int]


state = SimulatorState(
    memory=Memory(),
    rA=WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
    rX=WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0)),
    rI1=IndexRegister(False, Byte(0), Byte(0)),
    rI2=IndexRegister(False, Byte(0), Byte(0)),
    rI3=IndexRegister(False, Byte(0), Byte(0)),
    rI4=IndexRegister(False, Byte(0), Byte(0)),
    rI5=IndexRegister(False, Byte(0), Byte(0)),
    rI6=IndexRegister(False, Byte(0), Byte(0)),
    rJ=IndexRegister(False, Byte(0), Byte(0)),
    overflow=False,
    comparison_indicator=ComparisonIndicator.LESS,
)
