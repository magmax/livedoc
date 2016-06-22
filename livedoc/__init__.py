import os
import time
import logging
import copy

from .exceptions import LiveDocException
from .processors import (
    MarkdownProcessor,
    HtmlProcessor,
    CopyProcessor,
)
from livedoc.reports import Report

__ALL__ = ['LiveDoc']


logger = logging.getLogger(__name__)


class LiveDoc(object):
    STATUS_SUCCESS, STATUS_FAILURE, STATUS_ERROR = range(3)

    def __init__(self, processors=None, decorator=None, report=None):
        self.decorator = decorator
        self.report = report or Report()
        self.status = self.STATUS_SUCCESS
        self.processors = processors or [
            MarkdownProcessor(self.report),
            HtmlProcessor(self.report),
            CopyProcessor(self.report),
        ]

    def process(self, source, target):
        logger.info('Starting to process %s into %s', source, target)
        start = time.time()
        if os.path.isdir(source):
            self.process_directory(source, target)
        else:
            self.process_file(source, target)
        if self.decorator:
            self.decorator.copy_assets(target)
        logger.info('Finished in %.4f seconds' % (time.time() - start))

    def process_directory(self, source, target):
        for filename in os.listdir(source):
            name, ext = os.path.splitext(filename)
            fullsource = os.path.join(source, filename)
            fulltarget = os.path.join(target, "%s.html" % name)
            if os.path.isdir(fullsource):
                self.process_directory(fullsource, fulltarget)
                continue
            if os.path.isfile(fullsource):
                self.process_file(fullsource, fulltarget)
                continue
            logger.info('Ignoring file %s', fullsource)

    def process_file(self, source, target):
        if source.endswith(('~', '.py')):
            return
        logger.info('Processing file %s into %s', source, target)
        self.report.test_file(source)
        processor = self.choose_processor(source)
        fixtures = self._load_fixtures(source)
        directory = os.path.dirname(target)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(source) as fd:
            content, status = processor.process_stream(
                fd.read(),
                copy.deepcopy(fixtures)
            )
            self.status = max(self.status, status)
        if self.decorator:
            content = self.decorator.apply_to(content)

        with open(target, 'w+') as fd:
            fd.write(content)
        self.report.file_finish()

    def choose_processor(self, path):
        for processor in self.processors:
            if processor.test(path):
                return processor
        raise LiveDocException(
            'No valid processor was found for file %s',
            path
        )

    def _load_fixtures(self, source):
        filename, ext = os.path.splitext(source)
        filename += '.py'
        if not os.path.exists(filename):
            return {}
        variables = {}
        with open(filename) as fd:
            exec(fd.read(), variables)
        return variables
