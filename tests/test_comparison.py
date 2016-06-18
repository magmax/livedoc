import unittest
from livedoc.expressions import Comparison


class ComparisonOperatorEqualTest(unittest.TestCase):
    def test_equal(self):
        sut = Comparison('5', '5', '==')
        sut.evaluate({}, {})
        assert sut.success

    def test_not_equal(self):
        sut = Comparison('5', '10', '==')
        sut.evaluate({}, {})
        assert not sut.success

    def test_different_types(self):
        sut = Comparison('5', '"5"', '==')
        sut.evaluate({}, {})
        assert sut.success

    def test_different_types_conmutative(self):
        sut = Comparison('"5"', '5', '==')
        sut.evaluate({}, {})
        assert sut.success


class ComparisonOperatorDistinctTest(unittest.TestCase):
    def test_equal(self):
        sut = Comparison('5', '5', '!=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_not_equal(self):
        sut = Comparison('5', '10', '!=')
        sut.evaluate({}, {})
        assert sut.success


class ComparisonOperatorLtTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparison('5', '10', '<')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparison('5', '1', '<')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparison('5', '5', '<')
        sut.evaluate({}, {})
        assert not sut.success


class ComparisonOperatorLeTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparison('5', '10', '<=')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparison('5', '1', '<=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparison('5', '5', '<=')
        sut.evaluate({}, {})
        assert sut.success


class ComparisonOperatorGtTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparison('15', '5', '>')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparison('5', '15', '>')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparison('5', '5', '>')
        sut.evaluate({}, {})
        assert not sut.success


class ComparisonOperatorGeTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparison('15', '5', '>=')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparison('5', '15', '>=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparison('5', '5', '>=')
        sut.evaluate({}, {})
        assert sut.success


class ComparisonStringTest(unittest.TestCase):
    def test_to_string(self):
        sut = Comparison('5', '5', '>=')
        assert str(sut) == '5 >= 5'
