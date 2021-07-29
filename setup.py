#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = []
test_requirements = []

setup(
    author="Sebastian Kulla",
    author_email='sebastiankulla90@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A small tool that converts *.html-files to *.md-files",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='html_to_md_converter',
    name='html_to_md_converter',
    packages=find_packages(include=['html_to_md_converter', 'html_to_md_converter.*']),
    url='https://github.com/sebastiankulla/html_to_md_converter',
    version='0.1.1',
    zip_safe=False,
)
