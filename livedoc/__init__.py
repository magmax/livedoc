import os
import re
import tokenize
import logging
from io import StringIO, BytesIO
import markdown
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
        super().__init__()

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
            text = a.text or ''
            self.variables['TEXT'] = a.text
            self.variables['OUT'] = ''
            expr_type, left_expr, right_expr = self.split_expression(expression)
            if expr_type == 'assign':
                try:
                    r = eval(right_expr, self.variables, {})
                    self.variables[left_expr.strip()] = r
                    span.attrib['class'] = 'info'
                    span.text = text + (self.variables.get('OUT') or '')
                except Exception as e:
                    span.attrib['class'] = 'exception'
                    item = etree.Element("pre")
                    item.text = (
                        "The expression: `%s` returned %s"
                        % (right_expr.strip(), str(e))
                    )
                    item.attrib['class'] = 'exception'
                    # TODO: add here the variable list as hidden control
                    span.addnext(item)
                continue
            try:
                expression = expression.strip()
                r = eval(expression, self.variables, {})

                if r is None:
                    span.attrib['class'] = 'none'
                    span.text = text
                elif r:
                    span.attrib['class'] = 'success'
                    span.text = text
                else:
                    span.attrib['class'] = 'failure'
                    span.text = 'Expected {text} but was {r}'.format(
                        text=text,
                        r=r
                    )
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
                'meta',
                dict(
                    name="generator",
                    content="livedoc",
                )
            )
        )
        return head

    def split_expression(self, expression):
        for token in tokenize.tokenize(BytesIO(expression.encode()).readline):
            if token.type == tokenize.OP:
                _type = 'assign' if token.string == "=" else 'cmp'
                return _type, token.line[0:token.start[1]], token.line[token.end[1]:]
        return 'call', expression, None

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
    def __init__(self, processors=None, decorator=None):
        self.decorator = decorator
        self.processors = processors or [
            MarkdownProcessor(),
            HtmlProcessor(),
            CopyProcessor(),
        ]

    def process(self, source, target):
        logger.info('Starting to process %s into %s', source, target)
        self.process_directory(source, target)
        if self.decorator:
            self.decorator.copy_assets(target)

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
        if source.endswith('~'):
            return
        logger.info('Processing file %s into %s', source, target)
        processor = self.choose_processor(source)
        directory = os.path.dirname(target)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(source) as fd:
            content = processor.process_stream(fd.read())
        if self.decorator:
            content = self.decorator.apply_to(content)

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
