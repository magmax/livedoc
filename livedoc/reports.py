import logging

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

    def change_file(self, name):
        self.current_file = name
        self.current_test = self.DEFAULT_TESTNAME

    def change_test(self, name):
        self.current_test = name

    def file_finish(self):
        self.current_test = self.DEFAULT_TESTNAME
        self.current_file = None


class ConsoleReporter(Reporter):
    EMPTY = 'EMPTY'
    SUCCESS = 'OK'
    FAILURE = 'FAIL'
    ERROR = 'ERROR'

    def __init__(self, *args, **kwargs):
        self._status = self.EMPTY
        super().__init__(*args, **kwargs)

    def add_comparison(self, expression, resolved_expression, result):
        if self._status in (self.EMPTY, self.SUCCESS):
            self._status = self.SUCCESS if result else self.FAILURE

        logger.debug(
            '%s - %s (%s // %s) = %s' % (
                self.current_file,
                self.current_test,
                expression,
                resolved_expression,
                result,
            )
        )

    def add_exception(self, expression, exception):
        self._status = self.ERROR
        logger.warning("Exception raised: %s", exception)

    def change_test(self, name):
        if name == self.current_test:
            return
        self.print_status()
        self._status = self.EMPTY
        super().change_test(name)

    def file_finish(self):
        self.print_status()
        self._status = self.EMPTY
        super().file_finish()

    def print_status(self):
        if self._status == self.EMPTY:
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
