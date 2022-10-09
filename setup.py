#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as r:
    requirements = r.read()

with open('requirements_dev.txt') as r:
    test_requirements = r.read()

setup(
    author="Matias Andina",
    author_email='matiasandina@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="This Python package contains functions to get photometry data from a Tucker-Davis Technology (TDT) photomerty system and calculate dFF using methods developed by Martianova and colleagues.",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='phototdt',
    name='phototdt',
    packages=find_packages(include=['phototdt', 'phototdt.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/matiasandina/phototdt',
    version='0.0.1',
    zip_safe=False,
)
