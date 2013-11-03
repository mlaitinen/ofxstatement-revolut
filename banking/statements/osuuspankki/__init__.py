# Transaction type mapping for Osuuspankki statement parsers

TRANSACTION_TYPES = {
   "TILISIIRTO": "XFER",
   "PALVELUMAKSU": "SRVCHG",
   "PKORTTIMAKSU": "POS",
   "VIITESIIRTO": "PAYMENT",
   "PIKASIIRTO": "PAYMENT"
}

#   Other types available: 'CREDIT', 'DEBIT', 'INT', 'DIV', 'FEE', 'DEP',
#   'ATM', 'CHECK', 'CASH', 'DIRECTDEP', 'DIRECTDEBIT', 'REPEATPMT', 'OTHER'

# PARSER LIST

PARSERS = (".parser_corporate_2013",)
