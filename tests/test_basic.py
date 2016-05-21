import unittest
from livedoc import LiveDoc

class Fixtures(object):
    def ldfix_foo(self):
        return 5


class BasicUsage(unittest.TestCase):
    valid_html = (
        'assign [Bilbo Baggins](- "name = TEXT") '
        'and return [Bilbo Baggins](- "TEXT == name")'
    )
    invalid_html = (
        'assign [Bilbo Baggings](- "name = TEXT") '
        'and not return [Frodo Baggins](- "TEXT == name")'
    )
    expression_html = (
        'assign [Bilbo Baggins](- "name = TEXT") '
        'and return [BILBO BAGGINS](- "TEXT == name.upper()")'
    )

    def test_variable_assignment_and_echo(self):
        sut = LiveDoc(self.valid_html)
        assert 'success' in sut.render(Fixtures())

    def test_variable_assignment_and_echo_with_shortcut(self):
        sut = LiveDoc(self.valid_html)
        assert 'success' in sut.render(Fixtures())

    def test_variable_assignment_and_failure(self):
        sut = LiveDoc(self.invalid_html)
        assert 'failure' in sut.render(Fixtures())

    def test_assign_expression_to_variable(self):
        sut = LiveDoc(self.expression_html)
        assert 'success' in sut.render(Fixtures())

    def test_raising_exception (self):
        sut = LiveDoc('[ ](- "a = 5 / 0")')
        result = sut.render(Fixtures())
        assert 'exception' in result
        assert 'division by zero' in result

    def test_can_call_fixtures(self):
        fixtures = Fixtures()
        sut = LiveDoc('[ ](- "a = foo()")')
        result = sut.render(fixtures)
        assert sut.variables['a'] == fixtures.ldfix_foo()
