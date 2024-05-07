from hashlib import md5
from typing import Optional, Any, List

from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import StatementLine, Currency, Statement, InvestStatementLine

TRANSACTION_TYPES = {
    "TRANSFER": "XFER",
    "CARD_PAYMENT": "POS",
    "CARD_REFUND": "POS",
    "FEE": "FEE",
    "TOPUP": "DEP",
    "EXCHANGE": "XFER",
    "ATM": "ATM",
    "FEE": "FEE",
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
        "fees": 6,
        "currency": 7,
    }

    def parse_currency(self, value: Optional[str], field: str) -> Currency:
        return Currency(symbol=value)

    def parse_value(self, value: Optional[str], field: str) -> Any:
        value = value.strip() if value else value
        if field == "trntype":
            if value == "TRADE":
                return None

            # Default: Debit card payment
            return TRANSACTION_TYPES.get(value, "POS")
        elif field == "currency":
            return self.parse_currency(value, field)
        else:
            return super().parse_value(value, field)

    def is_investment_line(self, line: List[str]) -> bool:
        line_type = line[self.columns["Type"]]
        if line_type == "TRADE":
            column = self.columns.get("Product")
            return line[column] == "Investments" if column else False
        return False

    def parse_record_internal(self, line: List[str]) -> Optional[StatementLine]:
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

    def parse_record(self, line: List[str]) -> Optional[StatementLine|InvestStatementLine]:
        stmt_line = self.parse_record_internal(line)

        if not self.is_investment_line(line):
            return stmt_line

        invest_line = InvestStatementLine(id=stmt_line.id,
            date=stmt_line.date, memo=stmt_line.payee,
            amount=stmt_line.amount, security_id=stmt_line.id)

        if invest_line.memo == "Dividends" or invest_line.memo == "Dividend taxes":
            invest_line.trntype = "INCOME"
            invest_line.trntype_detailed = "DIV"
        elif invest_line.memo == "Investing money" or invest_line.amount < 0:
            invest_line.trntype = 'BUYSTOCK'
            invest_line.trntype_detailed = 'BUY'
            invest_line.units = 1
            invest_line.unit_price = abs(stmt_line.amount)
        elif invest_line.memo == "Merger and acquisition" and invest_line.amount > 0:
            invest_line.trntype = 'SELLSTOCK'
            invest_line.trntype_detailed = 'SELL'
            invest_line.units = 1
            invest_line.unit_price = stmt_line.amount
        else:
            stmt_line.trntype = "INT"
            return stmt_line

        return invest_line

    # noinspection PyUnresolvedReferences
    def parse(self) -> Statement:
        reader = self.split_records()

        for line in reader:
            self.cur_record += 1
            if not line:
                continue

            parsed = self.parse_record(line)
            if parsed:
                parsed.assert_valid()

                if isinstance(parsed, StatementLine):
                    self.statement.lines.append(parsed)
                elif isinstance(parsed, InvestStatementLine):
                    self.statement.invest_lines.append(parsed)

        # Generate fee transactions, if any fees exist
        for stmt_line in self.statement.lines:
            if not hasattr(stmt_line, "fees"):
                continue

            fee = self.parse_decimal(stmt_line.fees)
            if fee:
                fee_line = StatementLine()
                fee_line.amount = -fee
                fee_line.currency = stmt_line.currency
                fee_line.date = stmt_line.date
                fee_line.id = f"{stmt_line.id}-feex"
                fee_line.payee = "Revolut"
                fee_line.trntype = "FEE"
                fee_line.memo = f"Revolut fee for {stmt_line.payee}, {stmt_line.currency.symbol} {stmt_line.amount}"

                self.statement.lines.append(fee_line)

        return self.statement


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
