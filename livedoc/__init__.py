import os
import tokenize
import logging
import uuid
import traceback
import copy
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
        self._preprocess(tree)
        for a in tree.findall('//a[@href="-"]'):
            self.process_element(a)
            a.getparent().remove(a)
        return etree.tostring(tree).decode()

    def process_element(self, a):
        expression = a.attrib.get('title')
        self.variables['TEXT'] = a.text
        self.variables['OUT'] = ''
        expr = self.split_expression(expression)
        try:
            expr.evaluate(self.variables)
            a.addnext(expr.xml)
        except Exception as e:
            self._format_exception(a, expr, e)

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
        return expression_factory(expression)

    def _preprocess(self, tree):
        for table in tree.findall('//table'):
            head = table.find('thead')
            body = table.find('tbody')
            patterns = []
            for row in head.findall('tr'):
                for col in row.findall('th'):
                    a = col.find('a[@href="-"]')
                    if a is None:
                        patterns.append(None)
                        continue
                    patterns.append(a)
                    a.getparent().text = a.text
                    a.getparent().remove(a)
            if not any(x is not None for x in patterns):
                continue
            for row in body.findall('tr'):
                for n, col in enumerate(row.findall('td')):
                    pattern = patterns[n]
                    if pattern is None:
                        continue
                    element = copy.deepcopy(pattern)
                    element.text = col.text
                    col.text = ''
                    col.append(element)

    def _format_exception(self, anchor, expression, exception):
        msg = (
            "The expression: `%s` returned %s"
            % (str(expression), str(exception))
        )
        id = uuid.uuid4().hex
        button = etree.Element("button")
        button.attrib['class'] = "exception-button"
        button.attrib['onclick'] = "toggle_visibility('%s');" % id
        button.text = msg
        anchor.addnext(button)
        span = etree.Element("span")
        span.attrib['id'] = id
        span.attrib['class'] = 'exception'
        button.addnext(span)
        item = etree.Element("span")
        variables = '\n'.join(
            '\t%s = %s' % (k, self.variables[k])
            for k in sorted(self.variables)
            if not k.startswith('__')
        )
        item.text = (
            "%s\n%s\n\nContext:\n%s"
            % (msg, traceback.format_exc(), variables)
        )
        item.attrib['class'] = 'exception-text'
        span.append(item)


class Expression(object):
    def evaluate(self, variables):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    @property
    def xml(self):
        raise NotImplementedError()

    def autotype(self, value):
        for t in (int, float, str):
            try:
                return t(value)
            except ValueError:
                pass
        return value


class Assignment(Expression):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.result = None

    def evaluate(self, variables):
        r = eval(self.right, variables, {})
        self.result = self.autotype(r)
        variables[self.left] = self.result

    def __str__(self):
        return self.right

    @property
    def xml(self):
        span = etree.Element('span')
        span.attrib['class'] = 'info'
        span.text = str(self.result)
        return span


class Comparation(Expression):
    def __init__(self, left, right, operator):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = operator
        self.success = False
        self.text = None

    def evaluate(self, variables):
        self.left_result = eval(self.left, variables, {})
        self.right_result = eval(self.right, variables, {})
        self.success = self._operate()
        self.text = variables.get('TEXT')

    def _operate(self):
        if self.operator == '==':
            l = self.autotype(self.left_result)
            r = self.autotype(self.right_result)
            return l == r

    @property
    def decorator(self):
        return 'success' if self.success else 'failure'

    @property
    def xml(self):
        span = etree.Element('span')
        if self.success:
            span.attrib['class'] = 'success'
            span.text = str(self.text)
        else:
            span.attrib['class'] = 'failure'
            old_span = etree.Element('span')
            old_span.attrib['class'] = 'failure-expected'
            old_span.text = str(self.left_result)
            span.append(old_span)
            space_span = etree.Element('span')
            space_span.text = ' '
            span.append(space_span)
            new_span = etree.Element('span')
            new_span.attrib['class'] = 'failure-result'
            new_span.text = str(self.right_result)
            span.append(new_span)
        return span


class Call(Expression):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def evaluate(self, variables):
        eval(self.expression, variables, {})

    @property
    def xml(self):
        span = etree.Element('span')
        span.attrib['class'] = 'info'
        span.text = str(self.expression)
        return span

    def __str__(self):
        return self.expression


class Print(Expression):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
        self.result = None

    def evaluate(self, variables):
        self.result = eval(self.expression, variables, {})

    @property
    def output(self):
        return self.result

    @property
    def xml(self):
        span = etree.Element('span')
        span.attrib['class'] = 'info'
        span.text = str(self.result)
        return span


def expression_factory(expression):
    for token in tokenize.tokenize(BytesIO(expression.encode()).readline):
        if token.type == tokenize.OP:
            l = token.line[0:token.start[1]].strip()
            r = token.line[token.end[1]:].strip()
            if token.string == '=':
                if l == 'OUT':
                    return Print(r)
                else:
                    return Assignment(l, r)
            elif token.string not in ('+', '-', '*', '/', '%', '!',):
                return Comparation(l, r, token.string)
    return Call(expression)


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
