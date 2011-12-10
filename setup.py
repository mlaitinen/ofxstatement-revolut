from setuptools import setup, find_packages
import os

version = '1.2.1'

setup(name='banking.statements.osuuspankki',
      version=version,
      description="banking.statements plugin for Osuuspankki of Finland",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Petri Savolainen',
      author_email='petri.savolainen@koodaamo.fi',
      url='http://www.koodaamo.fi',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['banking', 'banking.statements'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'banking.statements',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
          [banking.statements.readerplugin]
          osuuspankki = banking.statements.osuuspankki:OPReaderPlugin
      """
      # -*- Entry points: -*-
      )
