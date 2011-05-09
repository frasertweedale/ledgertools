import datetime
import decimal

from .. import reader
from .. import xn

# These CSV readers are ripe for refactoring; provided they are headed by
# "Date", "Description", "Debit" and "Credit", the only difference is the
# how the date appears; a heuristic for deducing the date format should be
# easy to implement.
#
# i.e.
# - split by (-|/)
# - if one field of 8 digits, assume YYYYMMDD
# - if two fields of 2 digits, one field of 4, use posn of year to work out
# - string months should be easy to substitute
#
# However,
# - mm/dd vs dd/mm is harder to work out


class Reader(reader.CsvReader):
    def __init__(self, **kwargs):
        """Initialise the Ing Direct transaction reader

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
        datetuple = (date[6:], date[3:5], date[:2])
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
