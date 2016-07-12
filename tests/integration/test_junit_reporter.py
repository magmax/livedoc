import unittest
import tempfile
from unittest import mock
from livedoc.reports import JunitReporter
from lxml import etree

class JunitReporterTest(unittest.TestCase):
    def get_attribute(self, xml, attr):
        return xml.find('testsuite').attrib[attr]

    def get_suite_number(self, xml):
        return len(xml.findall('testsuite'))

    def get_suite_by_pos(self, xml, pos):
        return xml.findall('testsuite')[pos]

    def get_case_list(self, suite):
        return suite.findall('testcase')

    def get_errors(self, xml):
        return int(self.get_attribute(xml, 'errors'))

    def get_failures(self, xml):
        return int(self.get_attribute(xml, 'failures'))

    def get_tests(self, xml):
        return int(self.get_attribute(xml, 'tests'))

    def test_no_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)

            xml = sut.as_xml()

            assert 0 == self.get_suite_number(xml)

    def test_one_assert(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_comparison('foo', 'foo', True)
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)
            assert 1 == self.get_tests(xml)

            cases = self.get_case_list(self.get_suite_by_pos(xml, 0))
            assert 1 == len(cases)
            assert "foo" == cases[0].attrib['name']

    def test_two_asserts_in_the_same_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_comparison('foo', 'foo', True)
            sut.add_comparison('bar', 'bar', True)
            xml = sut.as_xml()
            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)
            assert 2 == self.get_tests(xml)

    def test_one_assert_failing(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_comparison('foo', 'foo', False)
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 1 == self.get_failures(xml)
            assert 1 == self.get_tests(xml)

            cases = self.get_case_list(self.get_suite_by_pos(xml, 0))
            assert 1 == len(cases)
            assert "foo" == cases[0].attrib['name']

    def test_assert_raises_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_exception('foo', Exception("foo"))
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 1 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)
            assert 1 == self.get_tests(xml)

            cases = self.get_case_list(self.get_suite_by_pos(xml, 0))
            assert 1 == len(cases)
            assert "foo" == cases[0].attrib['name']

    def test_one_of_any(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_comparison('foo', 'foo', True)
            sut.add_comparison('bar', 'bar', False)
            sut.add_exception('bazz', Exception("bazz"))
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 1 == self.get_errors(xml)
            assert 1 == self.get_failures(xml)
            assert 3 == self.get_tests(xml)

            cases = self.get_case_list(self.get_suite_by_pos(xml, 0))
            assert 3 == len(cases)

    def test_change_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.change_test("bar")
            sut.add_comparison('foo', 'foo', True)
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)
            assert 1 == self.get_tests(xml)

            cases = self.get_case_list(self.get_suite_by_pos(xml, 0))
            assert 1 == len(cases)
            assert "foo" == cases[0].attrib['name']

    def test_change_test_two_suites(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.add_comparison('foo', 'foo', True)
            sut.change_test("bar")
            sut.add_comparison('bazz', 'bazz', True)
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 2 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)


    def test_change_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            sut = JunitReporter(tmp)
            sut.file_finish()
            sut.change_file("foo")
            sut.add_comparison('bar', 'bar', True)
            xml = sut.as_xml()

            print(etree.tostring(xml))
            assert 1 == self.get_suite_number(xml)
            assert 0 == self.get_errors(xml)
            assert 0 == self.get_failures(xml)
            assert 1 == self.get_tests(xml)
