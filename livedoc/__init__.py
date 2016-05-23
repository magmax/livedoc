import os
import re
import markdown
import logging
from io import StringIO
from lxml import etree

__ALL__ = ['LiveDoc']


logger = logging.getLogger(__name__)


class LiveDocException(Exception):
    pass


class Processor(object):
    def test(self, filename):
        raise NotImplementedError('Abstract method')

    def process_stream(self, content):
        raise NotImplementedError('Abstract method')


class CopyProcessor(Processor):
    def test(self, filename):
        return True

    def process_stream(self, content):
        return content


class HtmlProcessor(Processor):
    def __init__(self):
        self.variables = {'__builtins__': {}}

    def test(self, filename):
        return filename.lower().endswith(('html', 'htm'))

    def process_stream(self, content):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        tree.getroot().insert(0, self.headers())
        for a in tree.findall('//a[@href="-"]'):
            span = etree.Element("span")
            a.addnext(span)
            a.getparent().remove(a)

            expression = a.attrib.get('title')
            self.variables['TEXT'] = a.text
            if self.is_assignment(expression):
                variable, sep, expression = expression.partition('=')
            else:
                variable = None
            expression = expression.strip()
            try:
                r = eval(expression, self.variables, {})
                if variable:
                    self.variables[variable.strip()] = r
                    status = 'info'
                else:
                    status = (
                        'none'
                        if r is None
                        else 'success'
                        if r
                        else 'failure'
                    )
                span.attrib['class'] = status
                data = self.variables.get('OUT') or ''
                if a.text:
                    data = a.text + data
                span.text = data
            except Exception as e:
                span.attrib['class'] = 'exception'
                item = etree.Element("pre")
                item.text = (
                    "The expression: `%s` returned %s"
                    % (expression, str(e))
                )
                item.attrib['class'] = 'exception'
                # TODO: add here the variable list as hidden control
                span.addnext(item)
        return etree.tostring(tree).decode()

    def headers(self):
        head = etree.Element('head')
        head.append(
            etree.Element(
                'link',
                dict(
                    rel="stylesheet",
                    href="custom.css",
                )
            )
        )
        return head

    def is_assignment(self, expression):
        return re.match('[\w\s\.\[\]]+=[^=]', expression)


class MarkdownProcessor(HtmlProcessor):
    def test(self, filename):
        return filename.lower().endswith(('md', 'markdown'))

    def process_stream(self, content):
        html = markdown.markdown(
            content,
            extensions=['markdown.extensions.tables'],
            output_format="xhtml5",
        )
        return super(MarkdownProcessor, self).process_stream(html)


class LiveDoc(object):
    def __init__(self, processors=None):
        self.processors = processors or [
            MarkdownProcessor(),
            HtmlProcessor(),
            CopyProcessor(),
        ]

    def process(self, source, target):
        logger.info('Starting to process %s into %s', source, target)
        for filename in os.listdir(source):
            name, ext = os.path.splitext(filename)
            fullsource = os.path.join(source, filename)
            fulltarget = os.path.join(target, "%s.html" % name)
            if os.path.isdir(fullsource):
                self.process(fullsource, fulltarget)
                continue
            if os.path.isfile(fullsource):
                self.process_file(fullsource, fulltarget)
                continue
            logger.info('Ignoring file %s', fullsource)

    def process_file(self, source, target):
        logger.info('Processing file %s into %s', source, target)
        processor = self.choose_processor(source)
        directory = os.path.dirname(target)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(source) as fd:
            content = processor.process_stream(fd.read())

        with open(target, 'w+') as fd:
            fd.write(content)

    def choose_processor(self, path):
        for processor in self.processors:
            if processor.test(path):
                return processor
        raise LiveDocException(
            'No valid processor was found for file %s',
            path
        )
