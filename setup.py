#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import os
import sys
import re
from setuptools import setup, find_packages



def get_version(*file_paths):
    """Retrieves the version from longclaw/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


VERSION = get_version("plume", "__init__.py")

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

with open('README.rst') as readme_file:
    README = readme_file.read()

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read()

REQUIREMENTS = [
    'marshmallow==2.13.6',
    'pymongo==3.5.1',
    'falcon==1.3.0',
    'simplejson==3.11.1'
]

SETUP_REQUIREMENTS = [
    'pytest-runner',
]

TEST_REQUIREMENTS = [
    'pytest',
]

setup(
    name='plume',
    version=VERSION,
    description="Easy webapps with falcon & mongodb",
    long_description=README + '\n\n' + HISTORY,
    author="James Ramm",
    author_email='jamessramm@gmail.com',
    url='https://github.com/JamesRamm/plume',
    packages=find_packages(include=['plume']),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='plume',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
)
