from typing import Tuple
from unittest import TestCase

from mix_simulator.byte import Byte
from mix_simulator.word import Word

from parameterized import parameterized  # type: ignore


class TestWord(TestCase):
    @parameterized.expand(
        [
            ((0, 5), (True, (1, 16, 3, 5, 4))),
            ((1, 5), (False, (1, 16, 3, 5, 4))),
            ((3, 5), (False, (3, 5, 4))),
            ((0, 3), (True, (1, 16, 3))),
            ((4, 4), (False, (5,))),
            ((0, 0), (True, ())),
        ]
    )
    def test_load_fields(
        self, test_input: Tuple[int, int], expected: Tuple[bool, Tuple[int, ...]]
    ) -> None:
        word = Word(True, Byte(1), Byte(16), Byte(3), Byte(5), Byte(4))
        actual = word.load_fields(*test_input)
        self.assertEqual(expected, actual)
