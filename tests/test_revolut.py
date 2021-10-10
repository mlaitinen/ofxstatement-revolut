import os
import datetime
from decimal import Decimal

from ofxstatement.plugins.revolut import RevolutPlugin
from ofxstatement.ui import UI

HERE = os.path.dirname(__file__)


def test_revolut_simple() -> None:
    plugin = RevolutPlugin(UI(), {})
    filename = os.path.join(HERE, "samples", "2021-october.csv")

    parser = plugin.get_parser(filename)
    statement = parser.parse()

    assert statement.account_id == "Revolut"

    assert len(statement.lines) == 7

    line0 = statement.lines[0]
    assert line0.amount == Decimal("-250")
    assert line0.currency.symbol == "EUR"
    assert line0.date == datetime.datetime(2021, 9, 5, 11, 32, 41)
    assert line0.payee == "transfer"
    assert line0.trntype == "XFER"
    assert line0.id == "7fb225d52ebec906c9f016a87afa3672"

    line1 = statement.lines[1]
    assert line1.amount == Decimal("-9.5")
    assert line1.currency.symbol == "EUR"
    assert line1.date == datetime.datetime(2021, 9, 5, 18, 22, 20)
    assert line1.payee == "company äöå"
    assert line1.trntype == "POS"
    assert line1.id == "b611755c1f6a53241aec217791399302"
