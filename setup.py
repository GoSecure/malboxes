"""pip/setuptools packaging

Based off https://github.com/pypa/sampleproject/blob/master/setup.py
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, remove
import shutil

from malboxes._version import __version__

here = path.abspath(path.dirname(__file__))

_tempfiles = []
def _prepare():
    """Preparing files for package"""
    # Here are files I want packaged but also in top-level directory as it is mostly
    # unrelated to actual build
    # pip will install data_files in an odd location so I copy them in package at
    # build time
    root_data_files = ['LICENSE', 'README.adoc', 'TODO.adoc', 'config-example.json']

    for f in root_data_files:
        _tempfiles.append(shutil.copy(path.join(here, f),
                                      path.join(here, 'malboxes')))

    # docs
    shutil.copytree(path.join(here, 'docs'), path.join(here, 'malboxes/docs'),
                    ignore=shutil.ignore_patterns('presentation'))

def _teardown():
    """Removing temporary files"""

    for f in _tempfiles:
        remove(path.join(here, f))

    shutil.rmtree(path.join(here, 'malboxes/docs'))

# Get the long description from the README file
# TODO process README to make it pure plaintext
with open(path.join(here, 'README.adoc'), encoding='utf-8') as f:
    long_description = f.read()

_prepare()

setup(
    name='malboxes',
    version=__version__,

    description='Build Malware VMs (boxes) or whole environments based on '
                'templates. Useful for analysts, sandboxes or honeypots. '
                'Leverages devops workflow with Vagrant and Packer.',
    long_description=long_description,

    url='https://github.com/gosecure/malboxes',

    author='Malboxes Team',
    author_email='obilodeau@gosecure.ca',

    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Information Technology',
        'Topic :: Security',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later '
        '(GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='virtual-machine malware reverse-engineering vagrant packer',

    # Once we have more code we'll migrate to a package and use find_packages()
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['appdirs', 'Jinja2'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    include_package_data = True,
    zip_safe = False,

    # install malboxes executable
    entry_points={
        'console_scripts': [
            'malboxes=malboxes:main',
        ],
    },
)

_teardown()
