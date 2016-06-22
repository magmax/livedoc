import tokenize
from io import BytesIO
from lxml import etree
from .reports import Report


class Expression(object):
    def __init__(self, report=None):
        self.report = report or Report()

    def evaluate(self, variables, fixtures):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    @property
    def failed(self):
        return False

    def as_xml(self):
        raise NotImplementedError()

    def autotype(self, value):
        for t in (int, float):
            if isinstance(value, t):
                return value
        for t in (int, float):
            try:
                return t(value.strip('\'"'))
            except ValueError:
                pass
        return str(value)


class Assignment(Expression):
    def __init__(self, left, right, **kwargs):
        super().__init__(**kwargs)
        self.left = left
        self.right = right
        self.result = None

    def evaluate(self, variables, fixtures):
        r = eval(self.right, fixtures, variables)
        self.result = self.autotype(r)
        variables[self.left] = self.result
        if self._setting_testname:
            self.report.test_name(self.result)

    def __str__(self):
        return self.right

    def as_xml(self):
        span = etree.Element('span')
        if not self._setting_testname:
            span.attrib['class'] = 'info'
        span.text = str(self.result)
        return span

    @property
    def _setting_testname(self):
        return self.left.strip() == 'TESTNAME'


class Comparison(Expression):
    def __init__(self, left, right, operator, **kwargs):
        super().__init__(**kwargs)
        self.left = left
        self.right = right
        self.operator = operator
        self.expression = "%s %s %s" % (left, operator, right)
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
        result = eval("l %s r" % self.operator, {'l': l, 'r': r})
        self.report.add_comparison(
            self.expression,
            '%s %s %s' % (l, self.operator, r),
            result
        )
        return result

    def as_xml(self):
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

    @property
    def failed(self):
        return not self.success

    def __str__(self):
        return "%s %s %s" % (self.left, self.operator, self.right)


class Call(Expression):
    css_class = 'call'

    def __init__(self, expression, **kwargs):
        super().__init__(**kwargs)
        self.expression = expression
        self.result = None

    def evaluate(self, variables, fixtures):
        self.result = eval(self.expression, fixtures, variables)

    def as_xml(self):
        span = etree.Element('span')
        span.attrib['class'] = self.css_class
        inner1 = etree.Element('span')
        inner1.attrib['class'] = '%s-expression' % self.css_class
        inner1.text = str(self.expression)
        span.append(inner1)
        inner2 = etree.Element('span')
        inner2.attrib['class'] = '%s-sep' % self.css_class
        inner2.text = ' '
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def expression_factory(expression, report=None):
    for token in tokenize.tokenize(BytesIO(expression.encode()).readline):
        if token.type == tokenize.OP:
            l = token.line[0:token.start[1]].strip()
            r = token.line[token.end[1]:].strip()
            if token.string == '=':
                if l == 'OUT':
                    return Print(r, report=report)
                else:
                    return Assignment(l, r, report=report)
            elif token.string not in '+-*/%!()[]{}':
                return Comparison(l, r, token.string, report=report)
    return Call(expression, report=report)
