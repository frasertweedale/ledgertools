import sys

from . import rule
from . import score
from . import ui


threshold = {
    'y':  8000,
    'y?': 6000,
    '?':  4000,
    'n?': 2000,
    'n':  0,
}


class XnDataError(Exception):
    """Missing or bogus data"""
    pass


class XnBalanceError(Exception):
    """Transaction does not balance"""
    pass


class Endpoint(object):
    def __init__(self, account, amount):
        self.account = account
        self.amount = amount

    def __repr__(self):
        return 'Endpoint({!r}, {!r})'.format(self.account, self.amount)


class Xn(object):
    def __init__(self, **kwargs):
        """Initialise the transaction object"""
        self.dropped = kwargs['dropped'] if 'dropped' in kwargs else False
        self.date = kwargs['date'] if 'date' in kwargs else None
        self.desc = kwargs['desc'] if 'desc' in kwargs else None
        self.amount = kwargs['amount'] if 'amount' in kwargs else None
        self.dst = kwargs['dst'] if 'dst' in kwargs else None
        self.src = kwargs['src'] if 'src' in kwargs else None

    def __repr__(self):
        return "xnlib.xn.Xn(\n" + '\n'.join(map(
            lambda x: '    {!r}: {!r}'.format(x, getattr(self, x)),
            ['date', 'desc', 'amount', 'src', 'dst', 'dropped']
        )) + ')\n'

    def __str__(self):
        """Convert to a Ledger transaction (no trailing blank line)"""
        self.balance()  # make sure the transaction balances

        s = "{0}/{1:02}/{2:02}  {3}\n".format(
            self.date.year, self.date.month, self.date.day, self.desc)
        for src in self.src:
            s += "  {0.account}  ${0.amount}\n".format(src)
        for dst in self.dst:
            s += "  {0.account}  ${0.amount}\n".format(dst)
        return s

    def check(self):
        """Check this transaction for completeness"""
        if not self.date:
            raise XnDataError("Missing date")
        if not self.desc:
            raise XnDataError("Missing description")
        if not self.dst:
            raise XnDataError("No destination accounts")
        if not self.src:
            raise XnDataError("No source accounts")
        if not self.amount:
            raise XnDataError("No transaction amount")

    def balance(self):
        """Check this transaction for correctness"""
        self.check()
        if not sum(map(lambda x: x.amount, self.src)) == -self.amount:
            raise XnBalanceError("Sum of source amounts "
                                 "not equal to transaction amount")
        if not sum(map(lambda x: x.amount, self.dst)) == self.amount:
            raise XnBalanceError("Sum of destination amounts "
                                 "not equal to transaction amount")
        return True

    def match_rules(self, rules):
        """Process this transaction against the given ruleset

        Returns a dict of fields with ScoreSet values, which may be empty.
        Notably, the rule processing will be shortcircuited if the Xn is
        already complete - in this case, None is returned.
        """
        try:
            self.check()
            return None
        except XnDataError:
            pass

        scores = {}

        for r in rules:
            outcomes = r.match(self)
            if not outcomes:
                continue
            for outcome in outcomes:
                if isinstance(outcome, rule.SourceOutcome):
                    key = 'src'
                elif isinstance(outcome, rule.DestinationOutcome):
                    key = 'dst'
                elif isinstance(outcome, rule.DescriptionOutcome):
                    key = 'desc'
                elif isinstance(outcome, rule.DropOutcome):
                    key = 'drop'
                else:
                    raise KeyError
                if key not in scores:
                    scores[key] = score.ScoreSet()  # initialise ScoreSet
                scores[key].append((outcome.value, outcome.score))

        return scores

    def apply_outcomes(self, outcomes, uio, dropped=False):
        """Apply the given outcomes to this rule.

        If user intervention is required, outcomes are not applied
        unless an xnlib.ui.UI is supplied.
        """
        if self.dropped and not dropped:
            # do nothing for dropped xn, unless specifically told to
            return

        if 'drop' in outcomes:
            highscore = score.score(outcomes['drop'].highest()[0])
            if highscore >= threshold['y']:
                # drop without prompting
                self.dropped = True
            elif highscore < threshold['n?']:
                # do NOT drop, and don't even ask
                pass
            else:
                uio.show('DROP was determined for transaction:')
                uio.show('')
                uio.show(self.summary())
                if highscore >= threshold['y?']:
                    default = True
                elif highscore >= threshold['?']:
                    default = None
                else:
                    default = False
                try:
                    self.dropped = uio.yn('DROP this transaction?', default)
                except ui.RejectWarning:
                    # we assume they mean "no"
                    pass

        if self.dropped and not dropped:
            # do nothing further for dropped xn, unless specifically told to
            return

        # account outcomes
        for outcome in ['src', 'dst']:
            if outcome not in outcomes or getattr(self, outcome):
                # no outcome, or the attribute was already set
                continue

            endpoints = []
            highest = outcomes[outcome].highest()
            try:
                highscore = score.score(highest[0])
                if len(highest) == 1:
                    if highscore >= threshold['y']:
                        # do it
                        endpoints = [
                            Endpoint(score.value(highest[0]), self.amount)
                        ]
                    else:
                        uio.show('Choose ' + outcome + ' for transaction:')
                        uio.show('')
                        uio.show(repr(self))

                        prompt = 'Is the account {0}?'.format(
                            score.value(highest[0])
                        )
                        if highscore >= threshold['y?']:
                            default = True
                        elif highscore >= threshold['?']:
                            default = None
                        else:
                            default = False
                        if uio.yn(prompt, default):
                            endpoints = [
                                Endpoint(
                                    score.value(highest[0]),
                                    self.amount
                                )
                            ]
                        else:
                            raise ui.RejectWarning('top score declined')
                else:
                    # tied highest score, let user pick
                    uio.show('Choose ' + outcome + ' for transaction:')
                    uio.show('')
                    uio.show(repr(self))

                    prompt = 'Choose an account'
                    endpoints = [
                        Endpoint(
                            uio.choose(prompt, map(score.value, highest)),
                            self.amount
                        )
                    ]

            except ui.RejectWarning:
                # user has rejected our offer(s)
                uio.show("\n")
                uio.show('Enter ' + outcome + ' endpoints:')
                try:
                    endpoints = []
                    remaining = self.amount
                    while remaining:
                        uio.show('\n${0} remaining'.format(remaining))
                        account = uio.text(
                            ' Enter account',
                            score.value(highest[0]) if highest else None
                        )
                        amount = uio.decimal(
                            ' Enter amount',
                            default=remaining,
                            lower=0,
                            upper=remaining
                        )
                        endpoints.append(Endpoint(account, amount))
                        remaining = self.amount \
                            - sum(map(lambda x: x.amount, endpoints))
                except ui.RejectWarning:
                    # bail out
                    sys.exit("bye!")

            # flip amounts if it was a src outcome
            if outcome == 'src':
                endpoints = map(
                    lambda x: Endpoint(x.account, -x.amount),
                    endpoints
                )

            # set endpoints
            setattr(self, outcome, endpoints)

        # TODO desc outcomes

    def complete(self, uio, dropped=False):
        """Query for all missing information in the transaction"""
        if self.dropped and not dropped:
            # do nothing for dropped xn, unless specifically told to
            return

        for end in ['src', 'dst']:
            if getattr(self, end):
                continue  # we have this information

            uio.show('\nEnter ' + end + ' for transaction:')
            uio.show('')
            uio.show(repr(self))
            try:
                endpoints = []
                remaining = self.amount
                while remaining:
                    account = uio.text(' Enter account', None)
                    amount = uio.decimal(
                        ' Enter amount',
                        default=remaining,
                        lower=0,
                        upper=remaining
                    )
                    endpoints.append(Endpoint(account, amount))
                    remaining = self.amount \
                        - sum(map(lambda x: x.amount, endpoints))
            except ui.RejectWarning:
                # bail out
                sys.exit("bye!")

            # flip amounts if it was a src outcome
            if end == 'src':
                endpoints = map(
                    lambda x: Endpoint(x.account, -x.amount),
                    endpoints
                )

            # set endpoints
            setattr(self, end, endpoints)

    def process(self, rules, uio):
        """Matches rules and applies outcomes"""
        self.apply_outcomes(self.match_rules(rules), uio)
