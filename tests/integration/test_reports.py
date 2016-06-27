import unittest
from livedoc.reports import Report


class ReportTest(unittest.TestCase):
    def test_no_initial_reporter(self):
        sut = Report()
        assert not sut.reporters

    def test_reporter_registry(self):
        mock_register = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register)
        assert [mock_register] == sut.reporters

    def test_reporter_registry_with_none(self):
        sut = Report()
        sut.register(None)
        assert not sut.reporters

    def test_testname_change(self):
        mock_register1 = unittest.mock.MagicMock()
        mock_register2 = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register1)
        sut.register(mock_register2)
        sut.test_name("foo")

        mock_register1.change_test.assert_called_once_with("foo")
        mock_register2.change_test.assert_called_once_with("foo")

    def test_file_change(self):
        mock_register1 = unittest.mock.MagicMock()
        mock_register2 = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register1)
        sut.register(mock_register2)
        sut.test_file("foo")

        mock_register1.change_file.assert_called_once_with("foo")
        mock_register2.change_file.assert_called_once_with("foo")

    def test_file_finish(self):
        mock_register1 = unittest.mock.MagicMock()
        mock_register2 = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register1)
        sut.register(mock_register2)
        sut.file_finish()

        mock_register1.file_finish.assert_called_once_with()
        mock_register2.file_finish.assert_called_once_with()

    def test_add_comparison(self):
        mock_register1 = unittest.mock.MagicMock()
        mock_register2 = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register1)
        sut.register(mock_register2)
        sut.add_comparison('expression', 'resolved', 'result')

        mock_register1.add_comparison.assert_called_once_with(
            'expression', 'resolved', 'result')
        mock_register2.add_comparison.assert_called_once_with(
            'expression', 'resolved', 'result')

    def test_add_exception(self):
        mock_register1 = unittest.mock.MagicMock()
        mock_register2 = unittest.mock.MagicMock()
        sut = Report()
        sut.register(mock_register1)
        sut.register(mock_register2)
        sut.add_exception('expression', 'exception')

        mock_register1.add_exception.assert_called_once_with(
            'expression', 'exception')
        mock_register2.add_exception.assert_called_once_with(
            'expression', 'exception')
