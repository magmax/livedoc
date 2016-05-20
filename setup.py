# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from livedoc import about


def read_file(filename):
    if os.path.exists(filename):
        with open(filename) as fd:
            return fd.read()
    return ''


class PyTest(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass to py.test"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest  # NOQA
        errno = pytest.main(self.pytest_args or ['--cov-report=term-missing'])
        sys.exit(errno)


setup(
    name=about.name,
    version=about.str_version,
    description=about.description,
    long_description=read_file('README.rst'),
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython'
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Code Generators',
        'Operating System :: OS Independent',
    ],
    keywords='livedoc documentation specification concordion',
    author='Miguel Ángel García',
    author_email='miguelangel.garcia@gmail.com',
    url=about.url,
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'factory_boy   >= 2.7.0',
        'pytest        >= 2.6.4',
        'pytest-cov    >= 2.2.1',

        'coverage      >= 4.1b3',
        'coveralls     >= 1.1',

        'flake8        >= 2.5.4',
    ],
    install_requires=[
        'markdown == 2.6.6',
        'lxml     == 3.6.0',
    ],
)