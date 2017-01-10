# Transaction type mapping for Osuuspankki statement parsers

TRANSACTION_TYPES = {
   "TILISIIRTO": "XFER",
   "PALVELUMAKSU": "FEE",
   "PKORTTIMAKSU": "POS",
   "VIITESIIRTO": "XFER",
   "PIKASIIRTO": "XFER",
   "ETUUS": "XFER",
   "AUTOMAATTINOSTO": "ATM",
   "MAKSUPALVELU": "REPEATPMT",
   "TALLETUSKORKO": "INT",
   "LÄHDEVERO": "FEE",
   "SUORAVELOITUS": "DIRECTDEBIT",
   "PANO": "DEP",
   "PERUUTUS": "DIRECTDEP",
   "VUOKRA": "PAYMENT",
   "VERONPALAUTUS": "DIRECTDEP",
   "PALKKA": "DIRECTDEP",
   "ARVOPAPERI": "OTHER"
}

#   Other types available: 'CREDIT', 'DEBIT', 'INT', 'DIV', 'FEE', 'DEP',
#   'ATM', 'CHECK', 'CASH', 'DIRECTDEP', 'DIRECTDEBIT', 'REPEATPMT', 'OTHER'


