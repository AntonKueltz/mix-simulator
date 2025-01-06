from typing import List, Tuple
from unittest import TestCase

from mix_simulator.byte import Byte, bytes_to_int, int_to_bytes

from parameterized import parameterized  # type: ignore


class TestByte(TestCase):
    @parameterized.expand(
        [
            ([Byte(0), Byte(0)], 0),
            ([Byte(63), Byte(63)], 4095),
            ([Byte(63), Byte(63), Byte(63)], 262_143),
            ([Byte(63), Byte(63), Byte(63), Byte(63)], 16_777_215),
            ([Byte(63), Byte(63), Byte(63), Byte(63), Byte(63)], 1_073_741_823),
            ([Byte(50), Byte(41)], 3241),
        ]
    )
    def test_bytes_to_int(self, test_input: Tuple[Byte, ...], expected: int) -> None:
        self.assertEqual(expected, bytes_to_int(test_input))

    @parameterized.expand(
        [
            (3241, 0, [Byte(41), Byte(50)]),
            (1_073_741_823, 0, [Byte(63), Byte(63), Byte(63), Byte(63), Byte(63)]),
            (3241, 5, [Byte(41), Byte(50), Byte(0), Byte(0), Byte(0)]),
        ]
    )
    def test_int_to_bytes(
        self, test_input: int, padding: int, expected: List[Byte]
    ) -> None:
        actual = int_to_bytes(test_input, padding=padding)
        self.assertEqual(expected, actual)
