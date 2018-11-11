# ofxstatement-revolut

[![Build Status](https://travis-ci.com/mlaitinen/ofxstatement-revolut.svg?branch=master)](https://travis-ci.com/mlaitinen/ofxstatement-revolut)

This is a plugin for use with [ofxstatement](https://github.com/kedder/ofxstatement) package. It implements
a parser for the Revolut CSV-formatted bank statement.

The CSV isn't very machine readable, so we need to do some ugly string
parsing to figure out the different field values.

Issue reports and pull requests welcome.

This module is based on the Osuuspankki ofxstatement parser found at
https://github.com/koodaamo/banking.statements.osuuspankki

## Installation

### From PyPI repositories
```
pip3 install ofxstatement-revolut
```

### From source
```
git clone https://github.com/mlaitinen/ofxstatement-revolut.git
python3 setup.py install
```

## Configuration options

| Option        | Description                                                                                                                                    |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| `account`     | Define the account of this bank statement                                                                                                      |
| `currency`    | The base currency of the account                                                                                                               |
| `date_format` | The date format in the bank statement. Note that you have to use double `%`-marks in the settings file like this: `date_format = %%b %%d, %%Y` |
