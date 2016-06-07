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

    def process_stream(self, content, fixtures):
        raise NotImplementedError('Abstract method')


class CopyProcessor(Processor):
    def test(self, filename):
        return True

    def process_stream(self, content, fixtures):
        return content


class HtmlProcessor(Processor):
    def __init__(self):
        self.variables = {'__builtins__': {}}
        super().__init__()

    def test(self, filename):
        return filename.lower().endswith(('html', 'htm'))

    def process_stream(self, content, fixtures):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        tree.getroot().insert(0, self.headers())
        self._preprocess(tree)
        for a in tree.findall('//a[@href="-"]'):
            self.process_element(a, fixtures)
            a.getparent().remove(a)
        return etree.tostring(tree).decode()

    def process_element(self, a, fixtures):
        expression = a.attrib.get('title')
        self.variables['TEXT'] = a.text
        self.variables['OUT'] = ''
        expr = self.split_expression(expression)
        try:
            expr.evaluate(self.variables, fixtures)
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
    def evaluate(self, variables, fixtures):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    @property
    def xml(self):
        raise NotImplementedError()

    def autotype(self, value):
        for t in (int, float):
            if isinstance(value, t):
                return value
        for t in (int, float):
            try:
                return t(value)
            except ValueError:
                pass
        return str(value)


class Assignment(Expression):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right
        self.result = None

    def evaluate(self, variables, fixtures):
        r = eval(self.right, fixtures, variables)
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


class Comparison(Expression):
    def __init__(self, left, right, operator):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = operator
        self.success = False
        self.text = None

    def evaluate(self, variables, fixtures):
        self.left_result = eval(self.left, fixtures, variables)
        self.right_result = eval(self.right, fixtures, variables)
        self.success = self._operate(fixtures)
        self.text = variables.get('TEXT')

    def _operate(self, fixtures):
        l = self.autotype(self.left_result)
        r = self.autotype(self.right_result)
        return eval("%s %s %s" % (l, self.operator, r), {}, {})

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

    def __str__(self):
        return "%s %s %s" % (self.left, self.operator, self.right)


class Call(Expression):
    css_class = 'call'

    def __init__(self, expression):
        super().__init__()
        self.expression = expression
        self.result = None

    def evaluate(self, variables, fixtures):
        self.result = eval(self.expression, fixtures, variables)

    @property
    def xml(self):
        span = etree.Element('span')
        span.attrib['class'] = self.css_class
        inner1 = etree.Element('span')
        inner1.attrib['class'] = '%s-expression' % self.css_class
        inner1.text = str(self.expression)
        span.append(inner1)
        inner2 = etree.Element('span')
        inner2.attrib['class'] = '%s-sep' % self.css_class
        inner2.text = str(self.result)
        span.append(inner2)
        inner2 = etree.Element('span')
        inner2.attrib['class'] = '%s-result' % self.css_class
        inner2.text = str(self.result)
        span.append(inner2)

        return span

    def __str__(self):
        return "%s => %s" % (self.expression, self.result)


class Print(Call):
    css_class = 'print'

    def __init__(self, expression):
        super().__init__(expression)


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
            elif token.string not in '+-*/%!()[]{}':
                return Comparison(l, r, token.string)
    return Call(expression)


class MarkdownProcessor(HtmlProcessor):
    def test(self, filename):
        return filename.lower().endswith(('md', 'markdown'))

    def process_stream(self, content, fixtures):
        html = markdown.markdown(
            content,
            extensions=['markdown.extensions.tables'],
            output_format="xhtml5",
        )
        return super(MarkdownProcessor, self).process_stream(html, fixtures)


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
        if source.endswith(('~', '.py')):
            return
        logger.info('Processing file %s into %s', source, target)
        processor = self.choose_processor(source)
        fixtures = self._load_fixtures(source)
        directory = os.path.dirname(target)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(source) as fd:
            content = processor.process_stream(fd.read(),
                                               copy.deepcopy(fixtures))
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

    def _load_fixtures(self, source):
        filename, ext = os.path.splitext(source)
        filename += '.py'
        if not os.path.exists(filename):
            return {}
        variables = {}
        with open(filename) as fd:
            exec(fd.read(), variables)
        return variables
