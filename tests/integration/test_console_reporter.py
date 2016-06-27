import unittest
from unittest import mock
from livedoc.reports import ConsoleReporter


class ReporterTest(unittest.TestCase):
    def test_initialization(self):
        sut = ConsoleReporter()

        assert sut._status == ConsoleReporter.NOT_SET

    @mock.patch('livedoc.reports.logger')
    def test_add_comparison_success(self, mock_logger):
        sut = ConsoleReporter()
        sut.change_file("filename")
        sut.change_test("testname")
        sut.add_comparison('expression', 'resolved', 'result')
        mock_logger.debug.assert_called_once_with(
            mock.ANY,
            'filename',
            'testname',
            'expression',
            'resolved',
            'result',
        )
        assert sut._status == sut.SUCCESS

    @mock.patch('livedoc.reports.logger')
    def test_add_comparison_failure(self, mock_logger):
        sut = ConsoleReporter()
        sut.change_file("filename")
        sut.change_test("testname")
        sut.add_comparison('expression', 'resolved', False)
        mock_logger.debug.assert_called_once_with(
            mock.ANY,
            'filename',
            'testname',
            'expression',
            'resolved',
            False,
        )
        assert sut._status == sut.FAILURE

    def test_add_comparison_failure_then_success(self):
        sut = ConsoleReporter()
        sut.change_file("filename")
        sut.change_test("testname")
        sut.add_comparison('expression', 'resolved', False)
        sut.add_comparison('expression', 'resolved', True)
        assert sut._status == sut.FAILURE

    @mock.patch('livedoc.reports.logger')
    def test_add_exception(self, mock_logger):
        sut = ConsoleReporter()
        sut.add_exception('expression', 'exception')
        mock_logger.warning.assert_called_once_with(
            mock.ANY,
            'exception',
        )
        assert sut._status == sut.ERROR

    @mock.patch('livedoc.reports.ConsoleReporter.print_status')
    def test_change_test_once(self, mock_print):
        sut = ConsoleReporter()
        sut.change_test("foo")

        assert sut._status == sut.NOT_SET
        mock_print.assert_called_once_with()

    @mock.patch('livedoc.reports.ConsoleReporter.print_status')
    def test_change_test_with_no_change(self, mock_print):
        sut = ConsoleReporter()
        sut.change_test("foo")
        sut.change_test("foo")

        assert sut._status == sut.NOT_SET
        mock_print.assert_called_once_with()

    @mock.patch('livedoc.reports.ConsoleReporter.print_status')
    def test_file_finish(self, mock_print):
        sut = ConsoleReporter()
        sut.file_finish()

        assert sut._status == sut.NOT_SET
        mock_print.assert_called_once_with()

    @mock.patch('livedoc.reports.logger')
    def test_printstatus_no_status(self, mock_logger):
        sut = ConsoleReporter()
        sut.print_status()
        assert not mock_logger.info.called
        assert not mock_logger.warning.called

    @mock.patch('livedoc.reports.logger')
    def test_printstatus_success(self, mock_logger):
        sut = ConsoleReporter()
        sut.add_comparison("expression", "resolved", True)
        sut.print_status()
        assert mock_logger.info.called
        assert not mock_logger.error.called

    @mock.patch('livedoc.reports.logger')
    def test_printstatus_failure(self, mock_logger):
        sut = ConsoleReporter()
        sut.add_comparison("expression", "resolved", False)
        sut.print_status()
        assert not mock_logger.info.called
        assert mock_logger.error.called
