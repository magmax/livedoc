import time
import uuid
import traceback
import copy
from io import StringIO
import markdown
from lxml import etree

from livedoc.expressions import expression_factory
from livedoc.theme import Theme


class Processor(object):
    SUCCESS, FAILURE, ERROR = range(3)

    def __init__(self, report):
        self.report = report

    def test(self, filename):
        raise NotImplementedError('Abstract method')

    def process_stream(self, content, fixtures):
        raise NotImplementedError('Abstract method')


class CopyProcessor(Processor):
    def test(self, filename):
        return True

    def process_stream(self, content, fixtures):
        return content, self.SUCCESS


class HtmlProcessor(Processor):
    def __init__(self,  theme=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variables = {'__builtins__': {}}
        self.theme = theme or Theme()

    def test(self, filename):
        return filename.lower().endswith(('html', 'htm'))

    def process_stream(self, content, fixtures):
        status = self.SUCCESS

        start = time.time()
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        headers = self.headers(tree)
        self._preprocess(tree)
        for a in tree.findall('//a[@href="-"]'):
            status = max(status, self.process_element(a, fixtures))
            a.getparent().remove(a)
        self._postprocess(tree, time.time() - start)
        doc = '\n'.join(self._extract_children(tree.find('/body')))
        html = self.theme.test_template.render(body=doc, headers=headers)
        return html, status

    def process_element(self, a, fixtures):
        status = self.SUCCESS
        expression = a.attrib.get('title')
        self.variables['TEXT'] = a.text
        self.variables['OUT'] = ''
        expr = self.split_expression(expression)
        try:
            expr.evaluate(self.variables, fixtures)
            a.addnext(expr.as_xml())
            status = self.FAILURE if expr.failed else self.SUCCESS
        except Exception as e:
            self._format_exception(a, expr, e)
            return self.ERROR
        return status

    def headers(self, tree):
        result = ['<meta name="generator" content="livedoc">']
        result.extend(self._extract_children(tree.find('/head')))
        return result

    def _extract_children(self, tree):
        if tree is None:
            return
        for child in tree.getchildren():
            yield etree.tostring(child).decode()

    def split_expression(self, expression):
        return expression_factory(expression, self.theme, self.report)

    def _preprocess(self, tree):
        self._preprocess_titles(tree)
        self._preprocess_tables(tree)

    def _postprocess(self, tree, elapsed):
        self._postprocess_addfooter(tree, elapsed)

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

    def _postprocess_addfooter(self, tree, elapsed):
        footer = etree.Element('div')
        footer.attrib['class'] = self.theme.get_classes('footer')
        hr = etree.Element('hr')
        span_1 = etree.Element('span')
        span_1.text = "Generated by "
        link = etree.Element('a')
        link.attrib['href'] = 'https://github.com/magmax/livedoc/'
        link.text = 'LiveDoc'
        span_2 = etree.Element('span')
        span_2.text = " in %.2f ms on %s" % (elapsed * 1000, time.asctime())
        footer.append(hr)
        footer.append(span_1)
        footer.append(link)
        footer.append(span_2)
        body = tree.find('//body')
        body.append(footer)

    def _format_exception(self, anchor, expression, exception):
        self.report.add_exception(expression, exception)
        msg = (
            "The expression: `%s` returned %s"
            % (str(expression), str(exception))
        )
        id = uuid.uuid4().hex
        button = etree.Element("button")
        button.attrib['class'] = self.theme.get_classes('exception_button')
        button.attrib['onclick'] = "toggle_visibility('%s');" % id
        button.text = msg
        anchor.addnext(button)
        span = etree.Element("span")
        span.attrib['id'] = id
        span.attrib['class'] = self.theme.get_classes('exception')
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
        item.attrib['class'] = self.theme.get_classes('exception_text')
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
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        body_etree = tree.find('//body')
        body = etree.tostring(body_etree).decode()
        return super(MarkdownProcessor, self).process_stream(body, fixtures)
