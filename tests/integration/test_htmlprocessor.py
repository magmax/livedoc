import unittest
from unittest import mock
from io import StringIO
from lxml import etree
from livedoc.processors import HtmlProcessor


class HtmlProcessorTest(unittest.TestCase):
    def test_matches_html_common_extensions(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
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
        sut = HtmlProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream("whatever", {})
        assert "whatever" in result
        assert "<body>" in result
        assert status == HtmlProcessor.SUCCESS

    def test_includes_meta(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream("whatever", {})
        tree = etree.parse(StringIO(result), etree.HTMLParser())
        root = tree.getroot()
        assert root[0].tag == 'head'
        assert any(
            x.attrib.get('name') == 'generator' and
            x.attrib.get('content') == 'livedoc'
            for x in root[0].findall('meta')
        )
        assert status == HtmlProcessor.SUCCESS

    @mock.patch('livedoc.processors.HtmlProcessor.split_expression')
    def test_basic_assignment(self, mock_split):
        mock_assignment = mock.Mock()
        mock_assignment.as_xml = mock.Mock(return_value=etree.Element('mock'))
        mock_split.return_value = mock_assignment

        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut.process_stream('<a href="-" title="foo = TEXT">bar</a>', {})

        assert mock_assignment.called_once_with('foo', 'bar')
        assert mock_assignment.evaluate.called_once_with({}, {})
        assert mock_assignment.as_xml.called

    @mock.patch('livedoc.processors.HtmlProcessor.split_expression')
    def test_basic_echo(self, mock_split):
        mock_print = mock.Mock()
        mock_print.as_xml = mock.Mock(return_value=etree.Element('mock'))
        mock_split.return_value = mock_print

        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut.process_stream('<a href="-" title="OUT = \'foo\'"></a>', {})

        assert mock_print.called_once_with("'foo'")
        assert mock_print.evaluate.called_once_with({}, {})
        assert mock_print.as_xml.called

    def test_basic_check_success(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream(
            '<a href="-" title="1 == 1">True</a>',
            {}
        )
        assert '<span class="success">True</span>' in result
        assert status == HtmlProcessor.SUCCESS

    def test_basic_check_failure(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        r, status = sut.process_stream('<a href="-" title="1 == 0">True</a>',
                                       {})
        assert '<span class="failure-expected">1</span><span>' in r
        assert '<span class="failure-result">0</span>' in r
        assert status == HtmlProcessor.FAILURE

    def test_full_assignment_and_check(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream(
            '<a href="-" title="a = TEXT">1</a>'
            '<a href="-" title="a == TEXT">1</a>',
            {}
        )
        assert '<span class="success">1</span>' in result
        assert status == HtmlProcessor.SUCCESS

    def test_statement_raises_an_exception(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream('<a href="-" title="a = 1/0"></a>',
                                            {})
        assert (
            'The expression: `1/0` returned division by zero'
            in result
        )
        assert 'Traceback (most recent call last):' in result
        assert status == HtmlProcessor.ERROR

    def test_basic_table_processing(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut.process_stream('''
<table>
  <thead>
    <tr>
      <th>a</th>
    </tr>
  </thead>
  <tbody>
      <td><a href="-" title="a=TEXT">5</a></td>
  </tbody>
</table>''', {})
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
        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut._preprocess(tree)
        result = etree.tostring(tree).decode()
        print(expected)
        print(result)
        assert '<th>a</th>' in result
        assert '<td><a href="-" title="a=TEXT">5</a></td>' in result

    def test_short_table_processing(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut.process_stream('''
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
</table>''', {})
        assert sut.variables['a'] == 5

    def test_short_table_processing_with_empty_patterns(self):
        sut = HtmlProcessor(report=unittest.mock.Mock())
        sut.process_stream('''
<table>
  <thead>
    <tr>
      <th>foo</th>
      <th><a href="-" title="a=TEXT">a</a></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>bar</td>
      <td>27</td>
    </tr>
  </tbody>
</table>''', {})
        assert sut.variables['a'] == 27
