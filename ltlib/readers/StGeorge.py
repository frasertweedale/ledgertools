# This file is part of ledgertools.
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

import datetime
import decimal

from .. import reader
from .. import xn


class Reader(reader.CsvReader):
    def __init__(self, **kwargs):
        """Initialise the St George transaction reader

        Takes an account argument which indicates the account that was
        transacted upon.
        """
        super(Reader, self).__init__(**kwargs)

        if 'account' not in kwargs:
            raise reader.DataError("Required account field was not provided")
        self.account = kwargs['account']

    def dict2xn(self, fields):
        xn_dict = {}

        # date
        date = fields['Date']
        datetuple = (date[:4], date[4:6], date[6:])
        xn_dict['date'] = datetime.date(*map(int, datetuple))

        # description
        xn_dict['desc'] = fields['Description']

        # amount
        if fields['Credit'] and fields['Debit']:
            # this doesn't seem right...
            raise reader.DataError("Credit and Debit field present; dubious.")
        xn_dict['amount'] = \
            decimal.Decimal(fields['Credit'] or fields['Debit'])

        if fields['Credit']:
            xn_dict['dst'] = [xn.Endpoint(self.account, xn_dict['amount'])]
        else:
            xn_dict['src'] = [xn.Endpoint(self.account, -xn_dict['amount'])]

        return xn.Xn(**xn_dict)
