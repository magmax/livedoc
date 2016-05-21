import re
import markdown
import unittest
from lxml import etree
from io import StringIO

__ALL__ = ['LiveDoc', 'TestCase']


class LiveDoc(object):
    def __init__(self, template):
        self.template = template

    def render(self, fixtures):
        html =  markdown.markdown(self.template)
        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(html), parser)
        variables = {'__builtins__': {}}
        for a in tree.findall('//a[@href="-"]'):
            expression = a.attrib.get('title')
            variables['TEXT'] = a.text
            if self.is_assignment(expression):
                variable, sep, expression = expression.partition('=')
                variables[variable.strip()] = eval(expression, variables, fixtures.__dict__)
                a.attrib['class'] = 'info'
                continue
            try:
                r = eval(expression, variables, fixtures.__dict__)
                status = 'info' if r is None else 'success' if r else 'failure'
                a.attrib['class'] = status
            except Exception as e:
                print(e)
        return etree.tostring(tree).decode()

    def is_assignment(self, expression):
        return re.match('[\w\s\.\[\]]+=[^=]', expression)

class TestCase(unittest.TestCase):
    def run(self, *args, **kwargs):
        with open('poc.md') as fd:
            livedoc = LiveDoc(fd.read())
        with open('poc.html', 'w+') as fd:
            fd.write(livedoc.render(self))
        return super().run(*args, **kwargs)
