import csv
import re
from datetime import datetime

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import StatementLine, BankAccount

KNOWN_COLUMNS = [
    "Completed Date",
    "Reference",
    "Description",
    "Paid Out (...)",
    "Paid In (...)",
    "Exchange Out",
    "Exchange In",
    "Balance (...)",
    "Exchange Rate",
    "Category",
    "Notes",
]

TRANSACTION_TYPES = {
   "To ": "XFER",
   "From ": "XFER",
   "Cash at ": "ATM",
   "Top-Up by": "DEP",
   "Payment from": "DEP",
}


class RevolutCSVStatementParser(CsvStatementParser):

    __slots__ = 'columns'

    date_format = "%b %d, %Y"

    def parse_datetime(self, value):
        try:
            parsed_datetime = datetime.strptime(value, "%B %d")
            parsed_datetime = datetime(datetime.now().year, parsed_datetime.month, parsed_datetime.day)
            return parsed_datetime
        except ValueError:
            pass

        try:
            return datetime.strptime(value, "%Y %B %d")
        except ValueError:
            pass

        return super().parse_datetime(value)

    def split_records(self):
        return csv.reader(self.fin, delimiter=';', quotechar='"')

    def parse_value(self, value, field):
        value = value.strip() if value else value
        if field == "bank_account_to":
            return BankAccount("", value)
        else:
            return super().parse_value(value, field)

    def parse_payee_memo(self, value):
        if 'FX Rate' in value:
            limit = value.find('FX Rate')
            payee = self.parse_value(value[0:limit], 'payee')
            memo = self.parse_value(value[limit:], 'memo')
            return payee, memo
        else:
            return self.parse_value(value, 'payee'), ''

    def parse_amount(self, value):
        if not value or not value.strip():
            return 0

        return self.parse_float(value.strip().replace(',', ''))

    def parse_record(self, line):
        # Free Headerline
        if self.cur_record <= 1:
            return None

        c = self.columns
        stmt_line = StatementLine()
        stmt_line.date = self.parse_datetime(line[c["Completed Date"]].strip())

        # Amount
        paid_out = -self.parse_amount(line[c["Paid Out (...)"]])
        paid_in = self.parse_amount(line[c["Paid In (...)"]])
        stmt_line.amount = paid_out or paid_in

        reference = line[c["Reference" if "Reference" in c.keys()
                           else "Description"]].strip()

        trntype = False
        for prefix, transaction_type in TRANSACTION_TYPES.items():
            if reference.startswith(prefix):
                trntype = transaction_type
                break

        if not trntype:
            trntype = 'POS'  # Default: Debit card payment

        # It's ... pretty ugly, but I see no other way to do this than parse
        # the reference string because that's all the data we have.
        stmt_line.trntype = trntype
        if trntype == 'POS':
            stmt_line.payee, stmt_line.memo = self.parse_payee_memo(reference)
        elif reference.startswith('Cash at '):
            stmt_line.payee, stmt_line.memo = self.parse_payee_memo(
                reference[8:])
        elif reference.startswith('To ') or reference.startswith('From '):
            stmt_line.payee = self.parse_value(
                reference[reference.find(' '):], 'payee'
            )
        else:
            stmt_line.memo = self.parse_value(reference, 'memo')

        # Notes
        if "Notes" in c.keys():
            if not stmt_line.memo:
                stmt_line.memo = u''
            elif len(stmt_line.memo.strip()) > 0:
                stmt_line.memo += u' '
            stmt_line.memo += u'({})'.format(line[c["Notes"]].strip())

        return stmt_line


class RevolutPlugin(Plugin):
    """Revolut"""

    def get_parser(self, fin):
        f = open(fin, "r", encoding='utf-8')
        signature = f.readline()

        # Get currency ISO code and remove it from header line
        ccy = re.sub(r'.*\(([A-Z]{3})\).*', r'\1', signature)[:3]
        signature = re.sub(r'\([A-Z]{3}\)', '(...)', signature)

        columns = [col.strip() for col in signature.split(';')]

        if "Completed Date" in columns \
            and "Paid Out (...)" in columns \
            and "Paid In (...)" in columns \
                and ("Reference" in columns or "Description" in columns):

            f.seek(0)
            parser = RevolutCSVStatementParser(f)
            parser.columns = {col: columns.index(col) for col in columns}
            if 'account' in self.settings:
                parser.statement.account_id = self.settings['account']
            else:
                parser.statement.account_id = 'Revolut - ' + ccy
            if 'currency' in self.settings:
                parser.statement.currency = self.settings['currency']
            else:
                parser.statement.currency = ccy
            if 'date_format' in self.settings:
                parser.date_format = self.settings['date_format']
            parser.statement.bank_id = self.settings.get('bank', 'Revolut')
            return parser

        # no plugin with matching signature was found
        raise Exception("No suitable Revolut parser "
                        "found for this statement file.")
