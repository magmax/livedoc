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

    def test_includes_meta(self):
        sut = HtmlProcessor()
        result = sut.process_stream("whatever")
        tree = etree.parse(StringIO(result), etree.HTMLParser())
        root = tree.getroot()
        assert root[0].tag == 'head'
        assert any(
            x.attrib.get('name') == 'generator' and
            x.attrib.get('content') == 'livedoc'
            for x in root[0].findall('meta')
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
        assert '<span class="info">foo</span>' in result

    def test_basic_check_success(self):
        sut = HtmlProcessor()
        result = sut.process_stream('<a href="-" title="1 == 1">True</a>')
        assert '<span class="success">True</span>' in result

    def test_basic_check_failure(self):
        sut = HtmlProcessor()
        r = sut.process_stream('<a href="-" title="1 == 0">True</a>')
        assert '<span class="failure-expected">1</span><span>' in r
        assert '<span class="failure-result">0</span>' in r

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
            'The expression: `1/0` returned division by zero'
            in result
        )
        assert 'Traceback (most recent call last):' in result

    def test_basic_table_processing(self):
        sut = HtmlProcessor()
        result = sut.process_stream('''
<table>
  <thead>
    <tr>
      <th>a</th>
    </tr>
  </thead>
  <tbody>
      <td><a href="-" title="a=TEXT">5</a></td>
  </tbody>
</table>''')
        assert sut.variables['a'] == 5

    def test_table_preprocessing(self):
        content = '''
<table>
  <thead>
    <tr>
      <th><a href="-" title="a=TEXT">a</a></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>5</td>
    </tr>
  </tbody>
</table>'''.strip()
        expected = '''
<table>
  <thead>
    <tr>
      <th>a</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="-" title="a=TEXT">5</a></td>
    </tr>
  </tbody>
</table>'''.strip()
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        sut = HtmlProcessor()
        sut._preprocess(tree)
        result = etree.tostring(tree).decode()
        assert expected in result


    def test_short_table_processing(self):
        sut = HtmlProcessor()
        result = sut.process_stream('''
<table>
  <thead>
    <tr>
      <th><a href="-" title="a=TEXT">a</a></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>5</td>
    </tr>
  </tbody>
</table>''')
        assert sut.variables['a'] == 5
