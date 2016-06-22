import unittest
from livedoc import MarkdownProcessor


class Issue_1_Test(unittest.TestCase):
    def test_variable_resolved_twice(self):
        text = (
            'This is just an [example](- "a=TEXT")'
            ' to show how [ ](- "OUT=a") is equal'
            ' to [example](- "a == TEXT").'
        )
        expected = (
            '<p>This is just an <span class="info">example</span>'
            ' to show how <span class="print">'
            '<span class="print-expression">a</span>'
            '<span class="print-sep"> </span>'
            '<span class="print-result">example</span>'
            '</span> is equal to '
            '<span class="success">example</span>'
        )
        md = MarkdownProcessor(report=unittest.mock.Mock())
        result = md.process_stream(text, {})
        assert expected in result
