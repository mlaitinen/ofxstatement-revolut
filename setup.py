#!/usr/bin/python3
"""Setup
#Note: To publish new version: `./setup.py sdist upload`
"""
import os
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import setup

import unittest

version = "2.0.3"

setup(name="ofxstatement-revolut",
      version=version,
      author="Miku Laitinen",
      author_email="miku@avoin.systems",
      url="https://github.com/mlaitinen/ofxstatement-revolut",
      description=("Bank statement parser for Revolut"),
      long_description=open("README.md").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      long_description_content_type="text/markdown",
      license="GPLv3",
      keywords=["ofx", "ofxstatement", "banking", "statement", "revolut"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 3",
          "Natural Language :: English",
          "Topic :: Office/Business :: Financial :: Accounting",
          "Topic :: Utilities",
          "Environment :: Console",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
      packages=find_packages("src"),
      package_dir={"": "src"},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          "ofxstatement": [
              "revolut = ofxstatement.plugins.revolut:RevolutPlugin",
          ]
      },
      install_requires=["ofxstatement>=0.7.2"],
      extras_require={"test": ["pytest"]},
      include_package_data=True,
      zip_safe=True
      )
