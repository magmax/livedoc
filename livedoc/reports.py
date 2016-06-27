import os
import logging
import time
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


class TestSuite(object):
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.failures = []
        self.tests = 0
        self.skipped = 0
        self.time = None

    def add_failure(self, expression, resolved_expression, result):
        self.failures.append(
            'The expression `{exp}`, resolved as `{res}`,'
            ' returned `{ret}`, what is False.'
            .format(
                exp=expression,
                res=resolved_expression,
                ret=result,
            )
        )

    def add_error(self, expression, exception):
        self.errors.append(
            'The expression `{exp}` raised the exception:\n{exc}'
            .format(
                exp=expression,
                exc=exception,
            )
        )

    def as_xml(self):
        testsuite = etree.Element(
            'testsuite', dict(
                name=self.name,
                errors=str(len(self.errors)),
                failures=str(len(self.failures)),
                tests=str(self.tests),
                time=str(time),
            )
        )
        for failure in self.failures:
            item = etree.Element(
                'failure',
                dict(
                    message="Assertion failure",
                )
            )
            item.text = failure
            testsuite.append(item)
        for error in self.errors:
            item = etree.Element(
                'error',
                dict(
                    message="Error",
                )
            )
            item.text = error
            testsuite.append(item)

        return testsuite


class JunitReporter(Reporter):
    def __init__(self, outputdir, *args, **kwargs):
        self.outputdir = outputdir
        self._current = TestSuite(self.DEFAULT_TESTNAME)
        self._results = [self._current]
        self._time = time.time()
        super().__init__(*args, **kwargs)

    def add_comparison(self, expression, resolved_expression, result):
        self._current.tests += 1
        if not result:
            self._current.add_failure(
                expression,
                resolved_expression,
                result,
            )

    def add_exception(self, expression, exception):
        self._current.add_error(expression, exception)

    def file_finish(self):
        filename = os.path.join(
            self.outputdir,
            "%s.xml" % self.current_file
        )
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'w+') as fd:
            fd.write(etree.tostring(self.as_xml()).decode())
        super().file_finish()

    def as_xml(self):
        tree = etree.Element('testsuites')
        for result in self._results:
            tree.append(result.as_xml())
        return tree
