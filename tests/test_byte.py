from unittest import TestCase

from mix_simulator.byte import Byte, bytes_to_int, int_to_bytes


class TestByte(TestCase):
    def test_bytes_to_int_limits(self) -> None:
        bs = [Byte(0), Byte(0)]
        self.assertEqual(0, bytes_to_int(bs))

        bs = [Byte(63), Byte(63)]
        self.assertEqual(4095, bytes_to_int(bs))

        bs = [Byte(63), Byte(63), Byte(63)]
        self.assertEqual(262_143, bytes_to_int(bs))

        bs = [Byte(63), Byte(63), Byte(63), Byte(63)]
        self.assertEqual(16_777_215, bytes_to_int(bs))

        bs = [Byte(63), Byte(63), Byte(63), Byte(63), Byte(63)]
        self.assertEqual(1_073_741_823, bytes_to_int(bs))

    def test_int_to_bytes(self) -> None:
        expected = [Byte(41), Byte(50)]
        actual = int_to_bytes(3241)
        self.assertEqual(expected, actual)

        expected = [Byte(63), Byte(63), Byte(63), Byte(63), Byte(63)]
        actual = int_to_bytes(1_073_741_823)
        self.assertEqual(expected, actual)

        expected = [Byte(41), Byte(50), Byte(0), Byte(0), Byte(0)]
        actual = int_to_bytes(3241, padding=5)
        self.assertEqual(expected, actual)
