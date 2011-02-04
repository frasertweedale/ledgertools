def account(pair):
    """Return the account part of an account, amount pair"""
    return pair[0]


def amount(pair):
    """Return the amount part of an account, amount pair"""
    return pair[1]


class XnDataError(Exception):
    """Missing or bogus data"""
    pass


class XnBalanceError(Exception):
    """Transaction does not balance"""
    pass


class Xn(object):
    def __init__(self, **kwargs):
        """Initialise the transaction object"""
        self.date = kwargs['date'] if 'date' in kwargs else None
        self.desc = kwargs['desc'] if 'desc' in kwargs else None
        self.amount = kwargs['amount'] if 'src' in kwargs else None
        self.dsts = kwargs['dsts'] if 'dsts' in kwargs else None
        self.src = kwargs['src'] if 'src' in kwargs else None

    def __str__(self):
        """Convert to a Ledger transaction (no trailing blank line)"""
        self.balance()  # make sure the transaction balances

        s = "{0}/{1:02}/{2:02}  {3}\n".format(
            self.date.year, self.date.month, self.date.day, self.desc)
        for dst in self.dsts:
            s += "  {0[0]}  ${0[1]:.2f}\n".format(dst)
        s += "  {0}\n".format(self.src)
        return s

    def check(self):
        """Check this transaction for completeness and correctness"""
        if not self.date:
            raise XnDataError("Missing date")
        if not self.desc:
            raise XnDataError("Missing description")
        if not self.dsts:
            raise XnDataError("No destination accounts")
        if not self.src:
            raise XnDataError("No source accounts")
        if not self.amount:
            raise XnDataError("No transaction amount")

        if not sum(map(amount, self.dsts)) == self.amount:
            raise XnDataError("Sum of destination amounts "
                              "not equal to transaction amount")

    def balance(self):
        """Balance the transaction"""
        self.check()
        # at the moment this returns true; the deduction from the source
        # account is implicitly the sum of payments to destinations
        # TODO lift this restriction
        return True
