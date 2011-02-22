from . import rule
from . import score


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
        return 'Endpoint({0}, {1})'.format(
            repr(self.account),
            repr(self.amount)
        )


class Xn(object):
    def __init__(self, **kwargs):
        """Initialise the transaction object"""
        self.date = kwargs['date'] if 'date' in kwargs else None
        self.desc = kwargs['desc'] if 'desc' in kwargs else None
        self.amount = kwargs['amount'] if 'amount' in kwargs else None
        self.dst = kwargs['dst'] if 'dst' in kwargs else None
        self.src = kwargs['src'] if 'src' in kwargs else None

    def __repr__(self):
        return "xnlib.xn.Xn(\n" + '\n'.join(map(
            lambda x: '    {0}: {1}'.format(repr(x), repr(getattr(self, x))),
            ['date', 'desc', 'amount', 'dst', 'src']
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
                else:
                    raise KeyError
                if key not in scores:
                    scores[key] = score.ScoreSet()  # initialise ScoreSet
                scores[key].append((outcome.value, outcome.score))

        return scores

    def apply_outcomes(self, outcomes, ui=None):
        """Apply the given outcomes to this rule.

        If user intervention is required, outcomes are not applied
        unless an xnlib.ui.UI is supplied.
        """

        # source outcomes
        if 'src' in outcomes and not self.src:
            highest = outcomes['src'].highest()
            if highest:
                highscore = score.score(highest[0])
                if len(highest) == 1:
                    if score.score(highest[0]) > 0:  # TODO threshold
                        self.src = [
                            Endpoint(score.value(highest[0]), -self.amount)
                        ]
                    else:
                        pass  # TODO UI confirm accept
            else:
                pass  # TODO UI provide options

        # destination outcomes
        if 'dst' in outcomes and not self.dst:
            highest = outcomes['dst'].highest()
            if highest:
                highscore = score.score(highest[0])
                if len(highest) == 1:
                    if score.score(highest[0]) > 0:  # TODO threshold
                        self.dst = [
                            Endpoint(score.value(highest[0]), self.amount)
                        ]
                    else:
                        pass  # TODO UI confirm accept
            else:
                pass  # TODO UI provide options

        # TODO desc outcomes

    def process(self, rules, ui=None):
        """Matches rules and applies outcomes"""
        outcomes = self.match_rules(rules)
        self.apply_outcomes(outcomes, ui=ui)
        #self.apply_outcomes(self.match_rules(rules), ui=ui)
