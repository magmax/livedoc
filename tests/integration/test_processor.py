import unittest
import pytest
from livedoc.processors import Processor


class CopyProcessorTest(unittest.TestCase):
    def test_process_everything(self):
        sut = Processor(report=unittest.mock.Mock())
        with pytest.raises(NotImplementedError):
            assert sut.test('foo.html')

    def test_process_returns_echo(self):
        sut = Processor(report=unittest.mock.Mock())
        with pytest.raises(NotImplementedError):
            assert sut.process_stream("whatever", {}) == "whatever"
