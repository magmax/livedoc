import uuid
import traceback
import copy
from io import StringIO
import markdown
from lxml import etree

from .expressions import expression_factory


class Processor(object):
    def __init__(self, report=None):
        self.report = report

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
    def __init__(self, *args, **kwargs):
        self.variables = {'__builtins__': {}}
        super().__init__(*args, **kwargs)

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
        return expression_factory(expression, self.report)

    def _preprocess(self, tree):
        self._preprocess_titles(tree)
        self._preprocess_tables(tree)

    def _preprocess_titles(self, tree):
        for i in range(1, 8):
            for title in tree.findall('//h%d' % i):
                link = etree.Element("a")
                link.attrib['href'] = '-'
                link.attrib['title'] = (
                    'TESTNAME = "%s"'
                    % title.text.replace('"', '\\\\"')
                )
                title.text = ''
                title.append(link)

    def _preprocess_tables(self, tree):
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
        self.report.add_exception(expression, exception)
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
