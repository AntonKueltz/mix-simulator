from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.register import IndexRegister, WordRegister

from parameterized import parameterized  # type: ignore


class TestWordRegister(TestCase):
    @parameterized.expand(
        [
            (
                (True, (Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))),
                (True, (1, 16, 3, 5, 4)),
            ),
            (
                (False, (Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))),
                (False, (1, 16, 3, 5, 4)),
            ),
            (
                (False, (Byte(3), Byte(5), Byte(4))),
                (False, (0, 0, 3, 5, 4)),
            ),
            (
                (True, (Byte(1), Byte(16), Byte(3))),
                (True, (0, 0, 1, 16, 3)),
            ),
            (
                (False, (Byte(5),)),
                (False, (0, 0, 0, 0, 5)),
            ),
            (
                (True, ()),
                (True, (0, 0, 0, 0, 0)),
            ),
        ]
    )
    def test_update(
        self,
        test_input: Tuple[bool, Tuple[Byte, ...]],
        expected: Tuple[bool, Tuple[int, int, int, int, int]],
    ) -> None:
        register = WordRegister(False, Byte(0), Byte(0), Byte(0), Byte(0), Byte(0))
        sign, data = test_input
        esign, (er1, er2, er3, er4, er5) = expected

        register.update(sign, *reversed(data))

        self.assertEqual(esign, register.sign)
        self.assertEqual(er1, register.r1)
        self.assertEqual(er2, register.r2)
        self.assertEqual(er3, register.r3)
        self.assertEqual(er4, register.r4)
        self.assertEqual(er5, register.r5)

    @parameterized.expand(
        [
            ((0, 5), (False, (6, 7, 8, 9, 0))),
            ((1, 5), (None, (6, 7, 8, 9, 0))),
            ((5, 5), (None, (0,))),
            ((2, 2), (None, (0,))),
            ((2, 3), (None, (9, 0))),
            ((0, 1), (False, (0,))),
        ]
    )
    def test_store_fields(
        self, test_input: Tuple[int, int], expected: Tuple[bool | None, Tuple[int, ...]]
    ) -> None:
        register = WordRegister(False, Byte(6), Byte(7), Byte(8), Byte(9), Byte(0))
        actual = register.store_fields(*test_input)
        self.assertEqual(expected, actual)


class TestIndexRegister(TestCase):
    @parameterized.expand(
        [
            ((True, (Byte(5), Byte(4))), (True, (5, 4))),
            ((False, (Byte(5),)), (False, (0, 5))),
            ((True, ()), (True, (0, 0))),
        ]
    )
    def test_update(
        self,
        test_input: Tuple[bool, Tuple[Byte, ...]],
        expected: Tuple[bool, Tuple[int, int]],
    ) -> None:
        register = IndexRegister(False, Byte(0), Byte(0))
        sign, data = test_input
        esign, (ei4, ei5) = expected

        register.update(sign, *reversed(data))

        self.assertEqual(esign, register.sign)
        self.assertEqual(ei4, register.i4)
        self.assertEqual(ei5, register.i5)

    @parameterized.expand(
        [
            ((0, 5), (True, (0, 0, 0, 9, 0))),
            ((1, 5), (None, (0, 0, 0, 9, 0))),
            ((5, 5), (None, (0,))),
            ((2, 2), (None, (0,))),
            ((2, 3), (None, (9, 0))),
            ((0, 1), (True, (0,))),
        ]
    )
    def test_store_fields(
        self, test_input: Tuple[int, int], expected: Tuple[bool | None, Tuple[int, ...]]
    ) -> None:
        register = IndexRegister(True, Byte(9), Byte(0))
        actual = register.store_fields(*test_input)
        self.assertEqual(expected, actual)

    def test_int(self) -> None:
        register = IndexRegister(False, Byte(1), Byte(16))
        self.assertEqual(80, int(register))
