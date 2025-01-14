from unittest import TestCase

from mix_simulator.operator import Operator


class TestOperator(TestCase):
    def test_conversion(self) -> None:
        for op in Operator:
            code, field = op.to_code_and_field()
            actual = Operator.from_code_and_field(code, field)

            self.assertEqual(op, actual)
