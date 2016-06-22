import os
import unittest
import tempfile
from livedoc.__main__ import main


class LivedocTest(unittest.TestCase):
    def test_example1(self):
        this_path = os.path.dirname(__file__)
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(this_path)),
            'examples',
            'example1',
        )
        with tempfile.TemporaryDirectory() as tmp:
            rc = main([example_path, '-o', tmp])
        assert rc == 0

    def test_example2(self):
        this_path = os.path.dirname(__file__)
        example_path = os.path.join(
            os.path.dirname(os.path.dirname(this_path)),
            'examples',
            'example2',
        )
        with tempfile.TemporaryDirectory() as tmp:
            rc = main([example_path, '-o', tmp])
        assert rc == 2
