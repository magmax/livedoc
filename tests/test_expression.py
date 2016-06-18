import unittest
from livedoc.expressions import Expression


class ExpressionAbstractTest(unittest.TestCase):
    def test_evaluate_is_abstract(self):
        sut = Expression()
        with self.assertRaises(NotImplementedError):
            sut.evaluate(None, None)

    def test_output_property_is_abstract(self):
        sut = Expression()
        with self.assertRaises(NotImplementedError):
            sut.output

    def test_xml_property_is_abstract(self):
        sut = Expression()
        with self.assertRaises(NotImplementedError):
            sut.xml


class ExpressionAutotype(unittest.TestCase):
    def test_detects_int(self):
        sut = Expression()
        result = sut.autotype('1')
        assert result == 1
        assert type(result) is int

    def test_detects_float(self):
        sut = Expression()
        result = sut.autotype('1.0')
        assert result == 1.0
        assert type(result) is float

    def test_detects_strings(self):
        sut = Expression()
        result = sut.autotype('whatever')
        assert result == 'whatever'
        assert type(result) is str

    def test_int_idempotent(self):
        sut = Expression()
        assert 1 == sut.autotype(1)

    def test_float_idempotent(self):
        sut = Expression()
        assert 3.14159 == sut.autotype(3.14159)
