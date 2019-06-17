# Copyright (c) 2019 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import sys
import itertools
from glob import glob


from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from gitpy_versioning import get_version


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


test = ['pytest', 'testfixtures', 'mock']
doc = ['sphinx']
install_requires = ['steelscript>=2.0',
                    'sleepwalker>=2.0',
                    'reschema==2.0']
setup_requires = ['pytest-runner']

setup(
    name='steelscript.scc',
    namespace_packages=['steelscript'],
    version=get_version(),
    author='Riverbed Technology',
    author_email='eng-github@riverbed.com',
    url='http://pythonhosted.org/steelscript',
    license='MIT',
    description='SteelScript support for SteelCentral Controller',
    long_description="""SteelScript for SteelCentral Controller
=======================================

SteelScript is a collection of libraries and scripts in Python and
JavaScript for interacting with Riverbed Technology devices.

This package contains python modules for interacting with a SteelCentral
Controller Device.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/

""",

    platforms='Linux, Mac OS, Windows',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Networking',
    ],

    packages=find_packages(exclude=('gitpy_versioning',)),
    include_package_data=True,

    data_files=(
        ('share/doc/steelscript/docs/scc', glob('docs/*')),
        ('share/doc/steelscript/examples/scc', glob('examples/*')),
    ),

    install_requires=install_requires,
    setup_requires=setup_requires,
    extras_require={'test': test,
                    'doc': doc,
                    'dev': [p for p in itertools.chain(test, doc)],
                    'all': []
                    },
    tests_require=test,
    cmdclass={'pytest': PyTest},
    entry_points={
        'portal.plugins': ['SCC = steelscript.scc.appfwk.plugin:SCCPlugin']}
)
