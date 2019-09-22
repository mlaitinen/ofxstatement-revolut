import os
import unittest
from tempfile import NamedTemporaryFile
import filecmp
from freezegun import freeze_time

from ofxstatement import configuration
from ofxstatement.tool import convert
from argparse import Namespace


class RevolutTest(unittest.TestCase):

    def load_configuration(self):
        here = os.path.dirname(__file__)
        cfname = os.path.join(here, 'samples', 'config.ini')
        return configuration.read(cfname)

    def test_configuration(self):
        config = self.load_configuration()
        self.assertEqual(config['revolut']['date_format'], '%Y-%m-%d')

    @freeze_time('2018-11-11 14:17:13')
    def test_statement_april2018(self):

        here = os.path.dirname(__file__)
        csvname = os.path.join(here, 'samples', '2018-april.csv')
        ofxname = os.path.join(here, 'samples', '2018-april.ofx')

        with NamedTemporaryFile() as output:
            convert(Namespace(
                type='revolut',
                input=csvname,
                output=output.name,
            ))

            self.assertTrue(filecmp.cmp(output.name, ofxname))

    @freeze_time('2019-09-22 14:17:13')
    def test_statement_september2019(self):

        here = os.path.dirname(__file__)
        csvname = os.path.join(here, 'samples', '2019-september.csv')
        ofxname = os.path.join(here, 'samples', '2019-september.ofx')

        with NamedTemporaryFile() as output:
            convert(Namespace(
                type='revolut',
                input=csvname,
                output=output.name,
            ))

            self.assertTrue(filecmp.cmp(output.name, ofxname))
