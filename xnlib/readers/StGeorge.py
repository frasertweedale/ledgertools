import datetime

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

        xn_dict['amount'] = float(fields['Credit'] or fields['Debit'])

        if fields['Credit']:
            xn_dict['dsts'] = [(self.account, xn_dict['amount'])]
        else:
            xn_dict['src'] = self.account

        return xn.Xn(**xn_dict)
