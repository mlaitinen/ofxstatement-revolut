from ofxstatement.parser import CsvStatementParser
import csv

from . import TRANSACTION_TYPES

SIGNATURE = "Kirjauspäivä;Arvopäivä;Määrä EUROA;Laji;Selitys;Saaja/Maksaja;\
Saajan tilinumero ja pankin BIC;Viite;Viesti;Arkistointitunnus"

class OPCsvStatementParser(CsvStatementParser):
    "parser the corporate acct statement, from 2013 on"
    
    mappings = {
       "date":1, "amount":2, "trntype":4, "payee":5,
       "acctto":6, "refnum":7, "memo":8, "id":9
    }

    date_format = "%d.%m.%Y"

    def split_records(self):
        return csv.reader(self.fin, delimiter=';')

    def parse_record(self, line):
        #Free Headerline
        if self.cur_record <= 1:
            return None

        #Change decimalsign from , to .
        line[2] = line[2].replace(',', '.')

        # Set transaction type
        line[4] = TRANSACTION_TYPES[line[4]]

        # fill statement line according to mappings
        sl = super(OPCsvStatementParser, self).parse_record(line)
        return sl
