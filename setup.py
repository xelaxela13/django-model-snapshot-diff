#!/usr/bin/env python
from setuptools import setup
from codecs import open


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Framework :: Django",
    "Framework :: Django :: 2.0",
    "Framework :: Django :: 2.1",
    "Framework :: Django :: 2.2",
    "Framework :: Django :: 3.0",
    "Framework :: Django :: 3.1",
]
setup(
    name="django-model-snapshot-diff",
    version="1.0.1",
    description="Django model snapshot difference",
    author="xelaxela13",
    author_email="xelaxela13@gmail.com",
    packages=["django_model_snapshot_diff"],
    url="https://github.com/xelaxela13/django-model-snapshot-diff",
    license="MIT",
    keywords="make django model snapshot with relations get difference",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
    install_requires=[
        "Django>=2.0",
        "deepdiff>=5.5.0"
    ],
)