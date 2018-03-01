from setuptools import setup, find_packages
import os

version = '1.3.3'

setup(name='banking.statements.osuuspankki',
      version=version,
      description="Account statement reader plugin for Osuuspankki of Finland",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Utilities',
        'Environment :: Console',
        'Operating System :: OS Independent',
        ],
      keywords=['ofxstatement','ofx'],
      author='Petri Savolainen',
      author_email='petri.savolainen@koodaamo.fi',
      url='https://github.com/koodaamo/banking.statements.osuuspankki',
      license='GPLv3',
      namespace_packages = ['banking', 'banking.statements'],
      packages = ['banking.statements.osuuspankki'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ofxstatement'
      ],
      entry_points="""
          [ofxstatement]
          op = banking.statements.osuuspankki.plugin:OPPlugin
      """
      )
