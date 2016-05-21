import re
import markdown
import unittest
import inspect
from io import StringIO
from lxml import etree

__ALL__ = ['LiveDoc', 'TestCase']


class LiveDoc(object):
    def __init__(self, template):
        self.template = template
        self.variables = {'__builtins__': {}}

    def render(self, fixtures):
        html = markdown.markdown(self.template)
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        fixtures = self.fixtures(fixtures)
        for a in tree.findall('//a[@href="-"]'):
            expression = a.attrib.get('title')
            self.variables['TEXT'] = a.text
            if self.is_assignment(expression):
                variable, sep, expression = expression.partition('=')
            else:
                variable = None
            expression = expression.strip()
            try:
                r = eval(expression, self.variables, fixtures)
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
                a.attrib['class'] = status
            except Exception as e:
                a.attrib['class'] = 'exception'
                item = etree.Element("pre")
                item.text = (
                    "The expression: `%s` returned %s"
                    % (expression, str(e))
                )
                item.attrib['class'] = 'exception'
                # TODO: add here the variable list as hidden control
                a.addnext(item)

        return etree.tostring(tree).decode()

    def is_assignment(self, expression):
        return re.match('[\w\s\.\[\]]+=[^=]', expression)

    def fixtures(self, fix_obj):
        prefix = 'ldfix_'

        def extract():
            for name, method in inspect.getmembers(fix_obj):
                if name.startswith(prefix):
                    yield (name[len(prefix):], method)
        return dict(extract())


class TestCase(unittest.TestCase):
    def run(self, *args, **kwargs):
        with open('poc.md') as fd:
            livedoc = LiveDoc(fd.read())
        with open('poc.html', 'w+') as fd:
            fd.write(livedoc.render(self))
        return super().run(*args, **kwargs)
