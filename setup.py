#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    buf = open(os.path.join(os.path.dirname(__file__), fname), 'rb').read()
    return buf.decode('utf8')


setup(
    name='git-hulahoop',
    version='0.1.dev1',
    description='Integrates hosted git-systems into your git cli.',
    long_description=read('README.md'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='https://github.com/mbr/git-hulahoop',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=['click', 'python-gitlab', 'volatile'],
    entry_points={
        'console_scripts': [
            'git-hulahoop = git_hulahoop.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ])
