import unittest
from unittest import mock
import os
import tempfile
from livedoc import LiveDoc


class LivedocTest(unittest.TestCase):
    def test_example1(self):
        processor = mock.Mock()
        processor.test = mock.Mock(return_value=True)
        processor.process_stream = mock.Mock(return_value="whatever")
        source = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'examples',
            'example1',
        )
        livedoc = LiveDoc(processors=[processor])
        with tempfile.TemporaryDirectory() as tmp:
            livedoc.process(source, tmp)
        print(processor.test.call_args_list)
        processor.test.assert_has_calls(
            [
                mock.call(os.path.join(source, 'document_1.html')),
                mock.call(os.path.join(source, 'document_2.md')),
            ],
            any_order=True
        )
        assert processor.process_stream.called