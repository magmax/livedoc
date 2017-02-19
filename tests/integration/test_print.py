import unittest
from livedoc.expressions import Print
from lxml import etree


class PrintTest(unittest.TestCase):
    def test_simple_evaluate(self):
        sut = Print('"whatever"')
        sut.evaluate({}, {})
        assert sut.result == "whatever"

    def test_var_replacement(self):
        sut = Print('isinstance(a, t)')
        sut.evaluate({'a': 5}, {'t': int})
        assert sut.result

    def test_xml(self):
        sut = Print('isinstance(1, int)')
        sut.evaluate({}, {})
        xml = etree.tostring(sut.as_xml()).decode()
        assert xml == (
            '<span class="print">'
            '<span class="print-expression">isinstance(1, int)</span>'
            '<span class="print-separator"> </span>'
            '<span class="print-result">True</span>'
            '</span>'
        )

    def test_to_string(self):
        sut = Print('isinstance(1, int)')
        sut.evaluate({}, {})
        assert str(sut) == 'isinstance(1, int) => True'
