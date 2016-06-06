import unittest
from livedoc import Comparation


class ComparationOperatorEqualTest(unittest.TestCase):
    def test_equal(self):
        sut = Comparation('5', '5', '==')
        sut.evaluate({}, {})
        assert sut.success

    def test_not_equal(self):
        sut = Comparation('5', '10', '==')
        sut.evaluate({}, {})
        assert not sut.success

    def test_different_types(self):
        sut = Comparation('5', '"5"', '==')
        sut.evaluate({}, {})
        assert sut.success

    def test_different_types_conmutative(self):
        sut = Comparation('"5"', '5', '==')
        sut.evaluate({}, {})
        assert sut.success


class ComparationOperatorDistinctTest(unittest.TestCase):
    def test_equal(self):
        sut = Comparation('5', '5', '!=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_not_equal(self):
        sut = Comparation('5', '10', '!=')
        sut.evaluate({}, {})
        assert sut.success


class ComparationOperatorLtTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparation('5', '10', '<')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparation('5', '1', '<')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparation('5', '5', '<')
        sut.evaluate({}, {})
        assert not sut.success


class ComparationOperatorLeTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparation('5', '10', '<=')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparation('5', '1', '<=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparation('5', '5', '<=')
        sut.evaluate({}, {})
        assert sut.success


class ComparationOperatorGtTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparation('15', '5', '>')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparation('5', '15', '>')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparation('5', '5', '>')
        sut.evaluate({}, {})
        assert not sut.success


class ComparationOperatorGeTest(unittest.TestCase):
    def test_against_greater(self):
        sut = Comparation('15', '5', '>=')
        sut.evaluate({}, {})
        assert sut.success

    def test_against_lower(self):
        sut = Comparation('5', '15', '>=')
        sut.evaluate({}, {})
        assert not sut.success

    def test_against_equal(self):
        sut = Comparation('5', '5', '>=')
        sut.evaluate({}, {})
        assert sut.success
