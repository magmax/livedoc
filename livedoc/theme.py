import os
import logging
import jinja2
import shutil

logger = logging.getLogger(__name__)


class Style(object):
    def __init__(self):
        self.info = 'info'
        self.success = 'success'
        self.failure = 'failure'
        self.failure_expected = 'failure-expected'
        self.failure_result = 'failure-result'
        self.call_span = 'call'
        self.call_expression = 'call-expression'
        self.call_separator = 'call-separator'
        self.call_result = 'call-result'
        self.print_span = 'print'
        self.print_expression = 'print-expression'
        self.print_separator = 'print-separator'
        self.print_result = 'print-result'
        self.footer = 'footer'
        self.exception_button = 'exception-button'
        self.exception = 'exception'
        self.exception_text = 'exception-text'

    def load(self, filename):
        with open(filename) as fd:
            for line in fd.readlines():
                if '=' not in line:
                    continue
                k, v = line.strip().split('=', 1)
                if hasattr(self, k):
                    setattr(self, k, v)
                else:
                    logger.warning(
                        'Unknown setting "%s" in file "%s"'
                        % (v, filename)
                    )

    def get(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        logger.warning("Required invalid style for %s" % name)
        return ''


class Theme(object):
    def __init__(self):
        self.style = Style()
        self.theme = None
        self._loaded = False

    def load(self, theme='simple'):
        for directory in reversed(self.theme_directories):
            filename = os.path.join(directory, 'styles.conf')
            if os.path.exists(filename):
                self.style.load(filename)
        self._loaded = True

    @property
    def theme_directories(self):
        prjdir = os.path.dirname(__file__)
        if self.theme:
            return [
                os.path.join('.', 'themes', self.theme),
                os.path.join(prjdir, 'themes', self.theme),
                os.path.join(prjdir, 'themes', 'livedoc'),
            ]
        return [os.path.join(prjdir, 'themes', 'livedoc')]

    @property
    def env(self):
        if not self._loaded:
            self.load()
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(list(self.theme_directories))
        )

    @property
    def test_template(self):
        return self.env.get_template('test.html')

    def get_classes(self, name):
        return self.style.get(name)

    def copy_assets(self, output):
        logger.debug('Copying assets to %s' % output)
        def copytree(source, target):
            for item in os.listdir(source):
                s = os.path.join(source, item)
                t = os.path.join(target, item)
                if os.path.isdir(s):
                    os.makedirs(t)
                    copytree(s, t)
                else:
                    shutil.copy2(s, t)
        for path in self.theme_directories:
            path = os.path.join(path, 'assets')
            if not os.path.exists(path):
                continue
            copytree(path, output)
