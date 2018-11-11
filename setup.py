#!/usr/bin/python3
"""Setup
#Note: To publish new version: `./setup.py sdist upload`
"""
import os
from setuptools import find_packages
from distutils.core import setup

version = "1.3.0"

setup(name='ofxstatement-revolut',
      version=version,
      author="Miku Laitinen",
      author_email="miku@avoin.systems",
      url="https://github.com/mlaitinen/ofxstatement-revolut",
      description=("Bank statement parser for Revolut"),
      long_description=open("README.md").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      license="GPLv3",
      keywords=["ofx", "ofxstatement", "banking", "statement", "revolut"],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Office/Business :: Financial :: Accounting',
          'Topic :: Utilities',
          'Environment :: Console',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=["ofxstatement", "ofxstatement.plugins"],
      entry_points={
          'ofxstatement': [
              'revolut = ofxstatement.plugins.revolut:RevolutPlugin',
          ]
      },
      install_requires=['ofxstatement'],
      include_package_data=True,
      zip_safe=True
      )
