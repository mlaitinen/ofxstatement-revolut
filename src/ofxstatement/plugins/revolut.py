import csv

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import StatementLine, BankAccount

SIGNATURES = [
    "Completed Date ; Reference ; Paid Out (EUR) ; Paid In (EUR) ; Exchange Out; Exchange In; Balance (EUR); Category",  # Pre Apr-2018
    "Completed Date ; Reference ; Paid Out (EUR) ; Paid In (EUR) ; Exchange Out; Exchange In; Balance (EUR); Category; Notes",  # Apr-2018
    "Completed Date ; Description ; Paid Out (EUR) ; Paid In (EUR) ; Exchange Out; Exchange In; Balance (EUR); Category; Notes",  # May-2018
]

TRANSACTION_TYPES = {
   "To ": "XFER",
   "From ": "XFER",
   "Cash at ": "ATM",
   "Top-Up by": "DEP",
}


class RevolutCSVStatementParser(CsvStatementParser):

    date_format = "%b %d, %Y"

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

        stmt_line = StatementLine()
        stmt_line.date = self.parse_datetime(line[0].strip())

        # Amount
        paid_out = -self.parse_amount(line[2])
        paid_in = self.parse_amount(line[3])
        stmt_line.amount = paid_out or paid_in

        reference = line[1].strip()
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

        # Notes (from Apr-2018)
        if len(line) > 8 and line[8].strip():
            if not stmt_line.memo:
                stmt_line.memo = u''
            elif len(stmt_line.memo.strip()) > 0:
                stmt_line.memo += u' '
            stmt_line.memo += u'({})'.format(line[8].strip())

        return stmt_line


class RevolutPlugin(Plugin):
    """Revolut"""

    def get_parser(self, fin):
        f = open(fin, "r", encoding='utf-8')
        signature = f.readline().strip()
        f.seek(0)
        if signature in SIGNATURES:
            parser = RevolutCSVStatementParser(f)
            if 'account' in self.settings:
                parser.statement.account_id = self.settings['account']
            if 'currency' in self.settings:
                parser.statement.currency = self.settings['currency']
            parser.statement.bank_id = self.settings.get('bank', 'Revolut')
            return parser

        # no plugin with matching signature was found
        raise Exception("No suitable Revolut parser "
                        "found for this statement file.")
