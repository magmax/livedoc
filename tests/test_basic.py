import unittest
from livedoc import LiveDoc


class BasicUsage(unittest.TestCase):
    def test_variable_assignment_and_echo(self):
        sut = LiveDoc('assign [Jane Smith](- "c:set=#name") and return [Jane Smith](- "?=#name")')
        assert 'success' in sut.render()

    def test_variable_assignment_and_echo_with_shortcut(self):
        sut = LiveDoc('assign [Jane Smith](- "#name") and return [Jane Smith](- "?=#name")')
        assert 'success' in sut.render()

    def test_variable_assignment_and_failure(self):
        sut = LiveDoc('assign [Jane Smith](- "c:set=#name") and not return [Jane Mully](- "?=#name")')
        assert 'failure' in sut.render()
