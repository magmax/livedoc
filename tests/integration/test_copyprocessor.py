import unittest
from livedoc import CopyProcessor


class CopyProcessorTest(unittest.TestCase):
    def test_process_everything(self):
        sut = CopyProcessor(report=unittest.mock.Mock())
        assert sut.test('foo.html')
        assert sut.test('foo.md')
        assert sut.test('foo.rst')
        assert sut.test('foo.py')
        assert sut.test('foo.txt')
        assert sut.test('whatever')

    def test_process_returns_echo(self):
        sut = CopyProcessor(report=unittest.mock.Mock())
        result, status = sut.process_stream("whatever", {})
        assert result == "whatever"
        assert status == CopyProcessor.SUCCESS
