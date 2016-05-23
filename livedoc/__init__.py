import os
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
        html = markdown.markdown(
            self.template,
            extensions=['markdown.extensions.tables'],
            output_format="xhtml5",
        )
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(html), parser)
        tree.getroot().insert(0, self.headers())
        fixtures = self.fixtures(fixtures)
        for a in tree.findall('//a[@href="-"]'):
            expression = a.attrib.get('title')
            self.variables['TEXT'] = a.text
            if 'OUT' in self.variables:
                self.variables.pop('OUT')
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
                if 'OUT' in self.variables:
                    a.text += self.variables['OUT']
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

    def headers(self):
        head = etree.Element('head')
        head.append(etree.Element('link', dict(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css")))
        return head

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
    ld_fixture = None
    ld_output = 'report'

    def test_livedoc(self):
        def test_file():
            classpath = inspect.getfile(self.__class__)
            classfile, _ = os.path.splitext(classpath)
            if self.ld_fixture is None:
                return "%s.md" % classfile
            if os.path.isabs(self.ld_fixture):
                return self.ld_fixture
            path, _ = os.path.split(classpath)
            return os.path.join(path, self.ld_fixture)

        fixture_file = test_file()
        fixture_path, fixture_filename_with_ext = os.path.split(fixture_file)
        fixture_filename, fixture_ext = os.path.splitext(fixture_filename_with_ext)
        fixture_fullpath = os.path.abspath(fixture_file)
        with open(fixture_fullpath) as fd:
            livedoc = LiveDoc(fd.read())
        if not os.path.exists(self.ld_output):
            os.makedirs(self.ld_output)
        with open(os.path.join(self.ld_output, "%s.html" % fixture_filename), 'w+') as fd:
            fd.write(livedoc.render(self))
