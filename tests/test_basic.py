import unittest
from livedoc import LiveDoc


class BasicUsage(unittest.TestCase):
    def test_variable_assignment_and_echo(self):
        sut = LiveDoc('assign [Jane Smith](- "#name") and return [Jane Smith](- "?=#name")')
        #assert 'return Jane Smith' in sut.render()
        assert 'success' in sut.render()
