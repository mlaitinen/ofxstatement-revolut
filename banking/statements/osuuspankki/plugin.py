# -*- encoding: utf-8 -*-
import csv
import decimal
from cStringIO import StringIO

from banking.statements.plugin import CSVReaderPlugin
from banking.statements.util import logger, ColumnMismatchError

from banking.statements import AccountEntryRecord as Record


# csv format, from circa 2004
class OPDialect(csv.Dialect):
   "Definitions for reading information from Osuuspankki account statements"

   delimiter = ";"
   doublequote = False
   escapechar = None
   lineterminator = "\r\n"
   quotechar = '"'
   quoting = csv.QUOTE_MINIMAL
   skipinitialspace = None


# circa 2004
MAPPING_V1 = {
   "date":'Tap.pv', "amount":u'Määrä\xa0EUROA' ,"description":"Selitys",
   "account": "Saajan tilinumero", "payee/recipient": "Saaja/Maksaja",
   "reference":"Viite", "message":"Viesti"
}

# in between, before BIC
MAPPING_V2 = {
   "date":u'Arvopäivä', "amount":u'Määrä\xa0EUROA',
   "description":u"Selitys", "account": u"Saajan tilinumero",
   "reference":u"Viite", "message":u"Viesti",
   "payee/recipient": u"Saaja/Maksaja"
}
# until at least 2011
MAPPING_V3 = {
   "date":u'Arvopäivä', "amount":u'Määrä\xa0EUROA',
   "description":u"Selitys", "account": u"Saajan tilinumero ja pankin BIC",
   "reference":u"Viite", "message":u"Viesti",
   "payee/recipient": u"Saaja/Maksaja"
}


class OPReaderPlugin(CSVReaderPlugin):
   ""

   # encoding the statement file is in
   ENCODING = "1252"

   def __init__(self, linestream, dialect=OPDialect(), debug=False):

      fixedstream = StringIO()
      for line in linestream:
         fixedstream.write(self.preprocess(line))
      linestream.close()
      fixedstream.seek(0)

      CSVReaderPlugin.__init__(self, fixedstream, debug=debug, dialect=dialect)

      for mapping in [MAPPING_V1, MAPPING_V2, MAPPING_V3]:
         mappedcolumns = [mapping[commonfield] for commonfield in Record._fields]
         if set(mappedcolumns).issubset(set(self.fieldnames)):
            self._mapping = mapping
            self._columns = [col.encode(self.ENCODING) for col in mappedcolumns]
            logger.debug("format ok: %s" % mappedcolumns)
            break
      else:
         raise Exception("bad format: %s" % str(self.fieldnames))

   def preprocess(self,row):
      return row.replace("&amp;amp;", "&")

   def can_parse(self, stream):
      "return True if this plugin can parse the stream"
      raise NotImplementedError

   def format_record(self, row):
      data = [row[colname] for colname in self._columns]
      data[1] = decimal.Decimal(data[1].replace(',','.'))
      return Record._make(data)

