import unittest
from livedoc.expressions import Call
from lxml import etree


class CallTest(unittest.TestCase):
    def test_simple_evaluate(self):
        sut = Call('isinstance(1, int)')
        sut.evaluate({}, {})
        assert sut.result

    def test_var_replacement(self):
        sut = Call('isinstance(a, t)')
        sut.evaluate({'a': 5}, {'t': int})
        assert sut.result

    def test_xml(self):
        sut = Call('isinstance(1, int)')
        sut.evaluate({}, {})
        xml = etree.tostring(sut.as_xml()).decode()
        assert xml == (
            '<span class="call">'
            '<span class="call-expression">isinstance(1, int)</span>'
            '<span class="call-separator"> </span>'
            '<span class="call-result">True</span>'
            '</span>'
        )

    def test_to_string(self):
        sut = Call('isinstance(1, int)')
        sut.evaluate({}, {})
        assert str(sut) == 'isinstance(1, int) => True'
