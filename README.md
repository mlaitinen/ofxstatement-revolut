ofxstatement-revolut
====================

This is a plugin for use with [ofxstatement](https://github.com/kedder/ofxstatement) package. It implements
a parser for the Revolut CSV-formatted bank statement.

The CSV isn't very machine readable, so we need to do some ugly string
parsing to figure out the different field values.

The date format in CSV file produced by Revolut depends on OS language
preferences. In case of date parsing error, edit `date_format` variable
in src/ofxstatement/plugins/revolut.py before installing.

Issue reports and pull requests welcome.

This module is based on the Osuuspankki ofxstatement parser found at
https://github.com/koodaamo/banking.statements.osuuspankki