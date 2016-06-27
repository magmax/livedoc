import unittest
from livedoc.reports import Reporter


class ReporterTest(unittest.TestCase):
    def test_initialization(self):
        sut = Reporter()
        assert sut.current_test == Reporter.DEFAULT_TESTNAME
        assert sut.current_file is None

    def test_add_comparison_is_abstract(self):
        sut = Reporter()
        with self.assertRaises(NotImplementedError):
            sut.add_comparison('expression', 'resolved', 'result')

    def test_add_exception_is_abstract(self):
        sut = Reporter()
        with self.assertRaises(NotImplementedError):
            sut.add_exception('expression', 'exception')

    def test_change_test(self):
        sut = Reporter()
        sut.change_test("foo")
        assert sut.current_test == "foo"
        assert sut.current_file is None

    def test_change_file(self):
        sut = Reporter()
        sut.change_test("foo")
        sut.change_file("bar")
        assert sut.current_test == Reporter.DEFAULT_TESTNAME
        assert sut.current_file == "bar"

    def test_file_finish(self):
        sut = Reporter()
        sut.change_file("bar")
        sut.change_test("foo")
        sut.file_finish()
        assert sut.current_test == Reporter.DEFAULT_TESTNAME
        assert sut.current_file is None
