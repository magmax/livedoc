import os
import logging
from lxml import etree

logger = logging.getLogger(__name__)


class Report(object):
    def __init__(self):
        self.reporters = []

    def test_name(self, name):
        for reporter in self.reporters:
            reporter.change_test(name)

    def test_file(self, name):
        for reporter in self.reporters:
            reporter.change_file(name)

    def file_finish(self):
        for reporter in self.reporters:
            reporter.file_finish()

    def add_comparison(self, expression, resolved_expression, result):
        for reporter in self.reporters:
            reporter.add_comparison(
                expression,
                resolved_expression,
                result,
            )

    def add_exception(self, expression, exception):
        for reporter in self.reporters:
            reporter.add_exception(
                expression,
                exception,
            )

    def register(self, reporter):
        if reporter is not None:
            self.reporters.append(reporter)


class Reporter(object):
    DEFAULT_TESTNAME = "<main>"

    def __init__(self):
        self.current_test = self.DEFAULT_TESTNAME
        self.current_file = None

    def add_comparison(self, expression, resolved_expression, result):
        raise NotImplementedError('Abstract method')

    def add_exception(self, expression, exception):
        raise NotImplementedError('Abstract method')

    def change_test(self, name):
        self.current_test = name

    def change_file(self, name):
        self.current_file = name
        self.current_test = self.DEFAULT_TESTNAME

    def file_finish(self):
        self.current_test = self.DEFAULT_TESTNAME
        self.current_file = None


class ConsoleReporter(Reporter):
    NOT_SET = 'NOT SET'
    SUCCESS = 'OK'
    FAILURE = 'FAIL'
    ERROR = 'ERROR'

    def __init__(self, *args, **kwargs):
        self._status = self.NOT_SET
        super().__init__(*args, **kwargs)

    def add_comparison(self, expression, resolved_expression, result):
        if self._status in (self.NOT_SET, self.SUCCESS):
            self._status = self.SUCCESS if result else self.FAILURE

        logger.debug(
            '%s - %s (%s // %s) = %s',
            self.current_file,
            self.current_test,
            expression,
            resolved_expression,
            result,
        )

    def add_exception(self, expression, exception):
        self._status = self.ERROR
        logger.warning("Exception raised: %s", exception)

    def change_test(self, name):
        if name == self.current_test:
            return
        self.print_status()
        self._status = self.NOT_SET
        super().change_test(name)

    def file_finish(self):
        self.print_status()
        self._status = self.NOT_SET
        super().file_finish()

    def print_status(self):
        if self._status == self.NOT_SET:
            return
        msg = '%s - %s... %s' % (
            self.current_file,
            self.current_test,
            self._status,
        )
        if self._status == self.SUCCESS:
            logger.info(msg)
        else:
            logger.error(msg)


class TestCase(object):
    def __init__(self, name):
        self.name = name
        self.time = None
        self.skipped = False
        self.failure = False
        self.error = False

    def set_failure(self, expression, resolved_expression, result):
        self.failure = (
            'The expression `{exp}`, resolved as `{res}`,'
            ' returned `{ret}`, what is False.'
            .format(
                exp=expression,
                res=resolved_expression,
                ret=result,
            )
        )

    def set_error(self, expression, exception):
        self.error = (
            'The expression `{exp}` raised the exception:\n{exc}'
            .format(
                exp=expression,
                exc=exception,
            )
        )

    def as_xml(self):
        test = etree.Element(
            'testcase',
            dict(
                name=self.name,
            )
        )
        if self.failure:
            failure = etree.Element('failure', {'message': "test failure"})
            failure.text = self.failure
            test.append(failure)
        if self.error:
            error = etree.Element('error', {'message': "test error"})
            error.text = self.error
            test.append(error)
        return test


class TestSuite(object):
    def __init__(self, name):
        self.name = name
        self._tests = []

    def add_test(self, test):
        self._tests.append(test)

    @property
    def tests(self):
        return len(self._tests)

    @property
    def failures(self):
        return sum(1 for x in self._tests if x.failure)

    @property
    def errors(self):
        return sum(1 for x in self._tests if x.error)

    @property
    def time(self):
        return sum(x.time for x in self._tests if x.time)

    def as_xml(self):
        if self._tests == []:
            return
        testsuite = etree.Element(
            'testsuite', dict(
                name=self.name,
                errors=str(self.errors),
                failures=str(self.failures),
                tests=str(self.tests),
                time=str(self.time),
            )
        )
        for test in self._tests:
            testsuite.append(test.as_xml())

        return testsuite


class JunitReporter(Reporter):
    def __init__(self, outputdir, *args, **kwargs):
        self.outputdir = outputdir
        self._current_suite = TestSuite(self.DEFAULT_TESTNAME)
        self._suites = [self._current_suite]
        super().__init__(*args, **kwargs)

    def add_comparison(self, expression, resolved_expression, result):
        test = TestCase(expression)

        if not result:
            test.set_failure(expression, resolved_expression, result)

        self._current_suite.add_test(test)

    def add_exception(self, expression, exception):
        test = TestCase(expression)
        test.set_error(expression, exception)

        self._current_suite.add_test(test)

    def change_test(self, name):
        self._current_suite = TestSuite(name)
        self._suites.append(self._current_suite)

    def file_finish(self):
        filename = os.path.join(
            self.outputdir,
            "%s.xml" % self.current_file
        )
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'w+') as fd:
            xml = self.as_xml()
            if xml:
                fd.write(etree.tostring(xml).decode())
        super().file_finish()

    def as_xml(self):
        tree = etree.Element('testsuites')
        for suite in self._suites:
            xml = suite.as_xml()
            if xml:
                tree.append(xml)
        return tree
