from hashlib import md5
from typing import Optional, Any, List

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import StatementLine, Currency, Statement

TRANSACTION_TYPES = {
    "TRANSFER": "XFER",
    "CARD_PAYMENT": "POS",
    "CARD_REFUND": "POS",
    "TOPUP": "DEP",
    "EXCHANGE": "OTHER",
    # "???": "ATM",  # TODO: What's Revolut's type for ATM transactions?
}


class RevolutCSVStatementParser(CsvStatementParser):

    __slots__ = 'columns'

    date_format = "%Y-%m-%d %H:%M:%S"

    mappings = {
        "trntype": 0,
        "date_user": 2,
        "date": 3,
        "payee": 4,
        "amount": 5,
        "fee": 6,
        "currency": 7,
    }

    def parse_currency(self, value: Optional[str], field: str) -> Currency:
        return Currency(symbol=value)

    def parse_value(self, value: Optional[str], field: str) -> Any:
        value = value.strip() if value else value
        if field == "trntype":
            # Default: Debit card payment
            return TRANSACTION_TYPES.get(value, "POS")
        elif field == "currency":
            return self.parse_currency(value, field)
        else:
            return super().parse_value(value, field)

    def parse_record(self, line: List[str]) -> Optional[StatementLine]:
        # Ignore the header
        if self.cur_record <= 1:
            return None

        c = self.columns

        # Ignore pending charges
        if line[c["State"]] != "COMPLETED":
            return None

        stmt_line = super().parse_record(line)

        # Generate a unique ID
        balance_content = line[c["Balance"]]
        balance = self.parse_float(balance_content) if balance_content else 0
        stmt_line.id = md5(f"{stmt_line.date}-{stmt_line.payee}-{stmt_line.amount}-{balance}".encode())\
            .hexdigest()

        return stmt_line

    # noinspection PyUnresolvedReferences
    def parse(self) -> Statement:
        statement = super().parse()

        # Generate fee transactions, if any fees exist
        for stmt_line in statement.lines:
            if not hasattr(stmt_line, "fee"):
                continue

            fee = self.parse_decimal(stmt_line.fee)
            if fee:
                fee_line = StatementLine()
                fee_line.amount = -fee
                fee_line.currency = stmt_line.currency
                fee_line.date = stmt_line.date
                fee_line.id = f"{stmt_line.id}-feex"
                fee_line.payee = "Revolut"
                fee_line.trntype = "FEE"
                fee_line.memo = f"Revolut fee for {stmt_line.payee}, {stmt_line.currency.symbol} {stmt_line.amount}"

                statement.lines.append(fee_line)

        return statement


class RevolutPlugin(Plugin):
    """Revolut"""

    def get_parser(self, filename: str) -> RevolutCSVStatementParser:
        f = open(filename, "r", encoding='utf-8')
        signature = f.readline()

        csv_columns = [col.strip() for col in signature.split(",")]
        required_columns = [
            "Type",
            "Started Date",
            "Completed Date",
            "Description",
            "Amount",
            "Currency",
            "Balance"
        ]

        if set(required_columns).issubset(csv_columns):

            f.seek(0)
            parser = RevolutCSVStatementParser(f)
            parser.columns = {col: csv_columns.index(col) for col in csv_columns}
            if 'account' in self.settings:
                parser.statement.account_id = self.settings['account']
            else:
                parser.statement.account_id = 'Revolut'
            if 'currency' in self.settings:
                parser.statement.currency = self.settings['currency']
            if 'date_format' in self.settings:
                parser.date_format = self.settings['date_format']
            parser.statement.bank_id = self.settings.get('bank', 'Revolut')
            return parser

        # no plugin with matching signature was found
        raise Exception("No suitable Revolut parser "
                        "found for this statement file.")
