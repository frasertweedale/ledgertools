# This file is part of ledgertools
# Copyright (C) 2011 Fraser Tweedale
#
# ledgertools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import datetime
import decimal
import re

from .. import reader
from .. import xn


date_delim = re.compile('-|/')


class Reader(reader.Reader):
    """CSV statement reader.

    This reader expects the field names to be provided as the first line
    of the file (TODO: make configurable).

    The file must provide "Date", "Description", "Debit" and "Credit" fields.
    The heuristic for interpreting the "Date" field is described in the
    parse_date() documentation.

    Since the assumption is that all transactions in a CSV file pertain to a
    particular account, this account must be supplied to the constructor.
    For a given transaction, the "to" or "from" field of the transaction object
    will be set to the given account according to whether the "Debit" or
    "Credit" field is used.
    """

    def __init__(self, **kwargs):
        """
        Takes an account argument which indicates the account that was
        transacted upon.
        """
        if 'account' not in kwargs:
            raise reader.DataError('Required account field was not provided')
        self.account = kwargs.pop('account')
        super(Reader, self).__init__(**kwargs)
        self.csvreader = csv.DictReader(self.file)

    def next(self):
        """Return the next transaction object.

        StopIteration will be propagated from self.csvreader.next()
        """
        return self.dict_to_xn(self.csvreader.next())

    def parse_date(self, date):
        """Parse the date and return a datetime object

        The heuristic for determining the date is:
         - if one field of 8 digits, YYYYMMDD
         - split by '-' or '/'
         - (TODO: substitute string months with their numbers)
         - if (2, 2, 4), DD-MM-YYYY (not the peculiar US order)
         - if (4, 2, 2), YYYY-MM-DD
         - ka-boom!

        The issue of reliably discerning between DD-MM-YYYY (sane) vs.
        MM-DD-YYYY (absurd, but Big In America), without being told what's
        being used,  is intractable.

        Return a datetime.date object.

        """
        if len(date) == 8:
            # YYYYMMDD
            return datetime.date(*map(int, (date[:4], date[4:6], date[6:])))
        try:
            # split by '-' or '/'
            parts = date_delim.split(date, 2)   # maxsplit=2
            if len(parts) == 3:
                if len(parts[0]) == 4:
                    # YYYY, MM, DD
                    return datetime.date(*map(int, parts))
                elif len(parts[2]) == 4:
                    # DD, MM, YYYY
                    return datetime.date(*map(int, reversed(parts)))
        # fail
        except TypeError, ValueError:
            raise reader.DataError('Bad date format: "{}"'.format(date))

    def dict_to_xn(self, fields):
        # normalise field names (strip whitespace)
        fields = dict(
            map(
                lambda (x, y): (x.strip(), y),
                fields.viewitems()
            )
        )

        xn_dict = {}  # dict that will be passed to Xn constructor

        # date
        xn_dict['date'] = self.parse_date(fields['Date'])

        # description
        xn_dict['desc'] = fields['Description']

        # amount
        if fields['Credit'] and fields['Debit']:
            # this doesn't seem right...
            raise reader.DataError('Credit and Debit field present; dubious.')
        xn_dict['amount'] = \
            decimal.Decimal(fields['Credit'] or fields['Debit'])

        if fields['Credit']:
            xn_dict['dst'] = [xn.Endpoint(self.account, xn_dict['amount'])]
        else:
            xn_dict['src'] = [xn.Endpoint(self.account, -xn_dict['amount'])]

        return xn.Xn(**xn_dict)
