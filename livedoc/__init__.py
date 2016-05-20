import markdown
import unittest
from lxml import etree
from io import StringIO

__ALL__ = ['LiveDoc', 'TestCase']


class LiveDoc(object):
    def __init__(self, template):
        self.template = template

    def render(self):
        html =  markdown.markdown(self.template)
        # create variables
        parser = etree.HTMLParser()
        tree   = etree.parse(StringIO(html), parser)
        variables = {}
        for a in tree.findall('//a'):
            if a.attrib.get('href') == '-':
                title = a.attrib.get('title')
                if title.startswith('#'):
                    variables[title] = a.text
        for a in tree.findall('//a'):
            if a.attrib.get('href') == '-':
                title = a.attrib.get('title')
                if title.startswith('?='):
                    command, sep, varname = title.partition('=')
                    print ('%s == %s' % (a.text, varname))
                    a.attrib['class'] = 'success' if a.text == variables.get(varname) else 'failure'


        '<p>assign Jane Smith and return <a href="-" title="?=#name">Jane Smith</a></p>'
        return etree.tostring(tree).decode()


class TestCase(unittest.TestCase):
    def run(self, *args, **kwargs):
        with open('poc.md') as fd:
            livedoc = LiveDoc(fd.read())
        with open('poc.html', 'w+') as fd:
            fd.write(livedoc.render(self))
        return super().run(*args, **kwargs)
