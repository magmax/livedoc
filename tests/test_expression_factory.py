import unittest
from livedoc import expression_factory, Print, Assignment, Comparison, Call


class ExpressionFactoryTest(unittest.TestCase):
    def test_simple_assignment(self):
        assert type(expression_factory("a = 3")) == Assignment

    def test_simple_print(self):
        assert type(expression_factory("OUT = 3")) == Print

    def test_simple_comparison(self):
        assert type(expression_factory("4 == 3")) == Comparison

    def test_simple_call(self):
        assert type(expression_factory("whatever()")) == Call
