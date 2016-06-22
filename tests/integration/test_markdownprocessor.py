import unittest
from livedoc import MarkdownProcessor


class MarkdownProcessorTest(unittest.TestCase):
    def test_matches_html_common_extensions(self):
        sut = MarkdownProcessor(report=unittest.mock.Mock())
        assert sut.test('foo.md')
        assert sut.test('foo.markdown')
        assert sut.test('foo.MD')
        assert sut.test('foo.Markdown')
        assert not sut.test('foo.html')
        assert not sut.test('foo.htm')
        assert not sut.test('FOO.HTML')
        assert not sut.test('FOO.HTM')
        assert not sut.test('foo.rst')
        assert not sut.test('foo.py')
        assert not sut.test('foo.txt')
        assert not sut.test('whatever')

    def test_process_returns_html(self):
        sut = MarkdownProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream("whatever", {})
        assert "whatever" in result
        assert "<body>" in result
        assert status == MarkdownProcessor.SUCCESS
