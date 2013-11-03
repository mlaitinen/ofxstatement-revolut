from ofxstatement.parser import CsvStatementParser
import csv


CORPORATE_2013 = [
   'Kirjauspäivä',
    'Arvopäivä', 'Määrä EUROA', 'Laji', 'Selitys', 'Saaja/Maksaja', 'Saajan tilinumero ja pankin BIC', 'Viite', 'Viesti', 'Arkistointitunnus']

"'Kirjauspäivä;Arvopäivä;Määrä EUROA;Laji;Selitys;Saaja/Maksaja;Saajan tilinumero ja pankin BIC;Viite;Viesti;Arkistointitunnus\n'"

class OPCsvStatementParser(CsvStatementParser):
    mappings = {"date": 1, "payee": 2, "trntype":3, "refnum":4, "memo": 5, "amount": 6}
    txntypes = {
        "TILISIIRTO": "XFER",
        "PALVELUMAKSU": "SRVCHG",
        "PKORTTIMAKSU": "POS",
        "VIITESIIRTO": "PAYMENT",
        "PIKASIIRTO": "PAYMENT"
    }
    #   ['CREDIT', 'DEBIT', 'INT', 'DIV', 'FEE', 'DEP', 'ATM', 'CHECK', 'CASH', 'DIRECTDEP', 'DIRECTDEBIT', 'REPEATPMT', 'OTHER']

    date_format = "%d.%m.%Y"

    def split_records(self):
        return csv.reader(self.fin, delimiter=';')

    def parse_record(self, line):
        #Free Headerline
        if self.cur_record <= 1:
            return None

        #Change decimalsign from , to .
        line[6] = line[6].replace(',', '.')

        # Set transaction type
        line[3] = self.txntypes[line[3]]

        # fill statement line according to mappings
        sl = super(OPCsvStatementParser, self).parse_record(line)
        return sl


