from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.instruction import Instruction
from mix_simulator.opcode import OpCode
from mix_simulator.register import IndexRegister, WordRegister
from mix_simulator.simulator import STATE

from parameterized import parameterized  # type: ignore


class TestIncrement(TestCase):
    def setUp(self) -> None:
        # set I1 to |+|1|36| = 100
        STATE.rI1.update(False, Byte(36), Byte(1))
        # set A to |+|0|0|0|15|40| = 1000
        STATE.rA.update(False, Byte(40), Byte(15))

    @parameterized.expand(
        [
            # INCA 200
            (
                Instruction(200, 0, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(18), Byte(48)),
            ),
            # INCA -200
            (
                Instruction(-200, 0, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(12), Byte(32)),
            ),
            # INCA 200,1
            (
                Instruction(200, 1, 0, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(20), Byte(20)),
            ),
            # DECA 200
            (
                Instruction(200, 0, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(12), Byte(32)),
            ),
            # DECA -200
            (
                Instruction(-200, 0, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(18), Byte(48)),
            ),
            # DECA 200,1
            (
                Instruction(200, 1, 1, OpCode.ATA),
                WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(10), Byte(60)),
            ),
        ]
    )
    def test_execute(self, test_input: Instruction, expected: WordRegister) -> None:
        test_input.execute()
        self.assertEqual(expected, STATE.rA)

    def test_overflow(self) -> None:
        # set A to |+|63|63|63|63|63| = INT_MAX
        STATE.rA.update(False, Byte(63), Byte(63), Byte(63), Byte(63), Byte(63))
        instruction = Instruction(1, 0, 0, OpCode.ATA)
        expected = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction.execute()

        self.assertEqual(expected, STATE.rA)
        self.assertTrue(STATE.overflow)

        # clear overflow toggle
        STATE.overflow = False

        # set A to |-|63|63|63|63|63| = INT_MAX
        STATE.rA.update(True, Byte(63), Byte(63), Byte(63), Byte(63), Byte(63))
        instruction = Instruction(1, 0, 1, OpCode.ATA)
        expected = WordRegister(True, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))

        instruction.execute()

        self.assertEqual(expected, STATE.rA)
        self.assertTrue(STATE.overflow)

    @parameterized.expand(
        [
            (OpCode.AT1, STATE.rI1, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT2, STATE.rI2, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT3, STATE.rI3, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT4, STATE.rI4, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT5, STATE.rI5, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT6, STATE.rI6, 0, IndexRegister(False, Byte(4), Byte(44))),
            (OpCode.AT1, STATE.rI1, 1, IndexRegister(True, Byte(1), Byte(36))),
            (OpCode.AT2, STATE.rI2, 1, IndexRegister(True, Byte(1), Byte(36))),
            (OpCode.AT3, STATE.rI3, 1, IndexRegister(True, Byte(1), Byte(36))),
            (OpCode.AT4, STATE.rI4, 1, IndexRegister(True, Byte(1), Byte(36))),
            (OpCode.AT5, STATE.rI5, 1, IndexRegister(True, Byte(1), Byte(36))),
            (OpCode.AT6, STATE.rI6, 1, IndexRegister(True, Byte(1), Byte(36))),
        ]
    )
    def test_execute_increment_index_register(
        self,
        opcode: OpCode,
        register: IndexRegister,
        variant: int,
        expected: IndexRegister,
    ) -> None:
        # set I1 to |+|1|36| = 100
        register.update(False, Byte(36), Byte(1))
        instruction = Instruction(100, 1, variant, opcode)

        instruction.execute()

        self.assertEqual(expected, register)
