import unittest
from livedoc import LiveDoc

class Fixtures(object):
    pass


class BasicUsage(unittest.TestCase):
    valid_html = (
        'assign [Bilbo Baggins](- "c:set=#name") '
        'and return [Bilbo Baggins](- "?=#name")'
    )
    invalid_html = (
        'assign [Bilbo Baggings](- "c:set=#name") '
        'and not return [Frodo Baggins](- "?=#name")'
    )
    expression_html = (
        'assign [Bilbo Baggins](- "c:set=#name") '
        'and return [BILBO BAGGINS](- "?=#name.upper()")'
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
