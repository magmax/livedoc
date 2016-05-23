import unittest
from io import StringIO
from lxml import etree
from livedoc import HtmlProcessor


class HtmlProcessorTest(unittest.TestCase):
    def test_matches_html_common_extensions(self):
        sut = HtmlProcessor()
        assert sut.test('foo.html')
        assert sut.test('foo.htm')
        assert sut.test('FOO.HTML')
        assert sut.test('FOO.HTM')
        assert not sut.test('foo.md')
        assert not sut.test('foo.rst')
        assert not sut.test('foo.py')
        assert not sut.test('foo.txt')
        assert not sut.test('whatever')

    def test_process_returns_html(self):
        sut = HtmlProcessor()
        result = sut.process_stream("whatever")
        assert "whatever" in result
        assert "<body>" in result

    def test_includes_css(self):
        sut = HtmlProcessor()
        result = sut.process_stream("whatever")
        tree = etree.parse(StringIO(result), etree.HTMLParser())
        root = tree.getroot()
        assert root[0].tag == 'head'
        assert any(
            x.attrib.get('href') == 'custom.css'
            for x in root[0].findall('link')
        )

    def test_basic_assignment(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="foo = TEXT">bar</a>')
        assert sut.variables['foo'] == 'bar'
        assert '<span class="info">bar</span>' in result

    def test_basic_echo(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="OUT = \'foo\'"></a>')
        assert '<span class="info">foo</span>' in result

    def test_basic_append(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="OUT=\'foo\'">bar</a>')
        assert '<span class="info">barfoo</span>' in result

    def test_basic_check_success(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="1 == 1">True</a>')
        assert '<span class="success">True</span>' in result

    def test_basic_check_failure(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="1 != 1">True</a>')
        assert '<span class="failure">True</span>' in result

    def test_full_assignment_and_check(self):
        sut = HtmlProcessor()
        result = sut.process_stream(
            '<a href="-" title="a = TEXT">1</a>'
            '<a href="-" title="a == TEXT">1</a>'
        )
        assert '<span class="success">1</span>' in result

    def test_statement_raises_an_exception(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="a = 1/0"></a>')
        assert (
            '<pre class="exception">'
            'The expression: `1/0` returned division by zero'
            '</pre>'
            in result
        )
