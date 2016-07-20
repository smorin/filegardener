#!/usr/bin/env python

import os
import sys
from glob import glob

# sys.path.insert(0, os.path.abspath('src'))

from filegardener import __version__, __author__
# import filegardener
try:
    from setuptools import setup
except ImportError:
    print ("filegardener now needs setuptools in order to build. ")
    print ("Install it using your package manager (usually python-setuptools) or via pip (pip install setuptools).")
    sys.exit(1)


from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    """
    This is the custom test command class to overwrite the default setuptools 
    test command behavior.
    
    This is instead running the module 'pytest' which will be auto installed
    by setup tools when you run 'python setup.py test'
    
    The following to commands are equivalent 
    
    python setup.py test -a "--durations=5"
    
    py.test --durations=5
    
    Reference: https://pytest.org/latest/goodpractices.html
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        
        self.pytest_args = ['--ignore=filegardener-virtualenv', '--ignore=filegardener-venv', '--ignore=tasks'] + self.pytest_args
        
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


from setuptools import find_packages

with open('README.rst') as file:
    long_description = file.read()


requires = ['Click']
test_requirements = ['pytest>=2.9.2', 'pytest-cov']


setup(
    name='filegardener',
    author=__author__,
    author_email='steve@stevemorin.com',
    version=__version__,
    url='http://TODO',
    include_package_data=True,
    install_requires=requires,
    entry_points='''
        [console_scripts]
        filegardener=filegardener:cli
    ''',
    py_modules=['filegardener'],
    # package_dir = {'':'.'},
    # packages=find_packages('.'),
    # packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "test"]),
    description='filegardener file utilities dedup, only file copy detection, empty dir detection',
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: POSIX :: BSD',        
    ],
    long_description=long_description,
	tests_require=test_requirements, 
	keywords=[
        'dedup', 'file cleanup', 'empy dirs', 'duplicate file detection',
    ],
    cmdclass={'test': PyTest},
)




