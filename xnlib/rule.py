class Condition(object):
    """A rule condition.

    Provides Condition.match(xn) which returns True if the rule
    matches the condition, otherwise False.
    """
    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value')
        super(Condition, self).__init__(*args, **kwargs)

    def match(self, xn):
        raise NotImplementedError  # subclasses must implement


class OperatorCondition(Condition):
    def __init__(self, *args, **kwargs):
        self.op = kwargs.pop('op')
        super(OperatorCondition, self).__init__(*args, **kwargs)


class SourceCondition(Condition):
    def match(self, xn):
        if xn.src is None:
            return False
        return filter(
            lambda src: src.account.startswith(self.value),
            xn.src
        )


class DestinationCondition(Condition):
    def match(self, xn):
        if xn.dst is None:
            return False
        return filter(
            lambda dst: dst.account.startswith(self.value),
            xn.dst
        )


class DescriptionCondition(Condition):
    def match(self, xn):
        if xn.desc is None:
            return False
        return self.value.search(xn.desc)


class AmountCondition(OperatorCondition):
    def match(self, xn):
        if xn.amount is None:
            return False
        return self.op(xn.amount, self.value)


class DateCondition(OperatorCondition):
    def match(self, xn):
        if xn.date is None:
            return False
        return self.op(xn.date, self.value)


class Outcome(object):
    """Specifies a rule outcome.

    A rule outcome consists of a value, and a numeric score associated
    with that value.
    """
    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value')
        self.score = kwargs.pop('score')
        super(Outcome, self).__init__(*args, **kwargs)


class SourceOutcome(Outcome):
    pass


class DestinationOutcome(Outcome):
    pass


class DescriptionOutcome(Outcome):
    pass


class Rule(object):
    """Rule providing match conditions and probabilistic outcomes

    When a transaction satisfies all conditions of a rule, the rule
    returns to the transaction a set of outcomes with probabilities.

    How these outcomes are used by the Xn is outside the scope of this
    class.
    """
    def __init__(self, *args):
        """Initialise the rule"""
        super(Rule, self).__init__()

        self.conditions = []
        self.outcomes = []

        for condition_or_outcome in args:
            if isinstance(condition_or_outcome, Condition):
                self.conditions.append(condition_or_outcome)
            elif isinstance(condition_or_outcome, Outcome):
                self.outcomes.append(condition_or_outcome)
            elif condition_or_outcome is not None:
                raise Exception  # TODO specialise

    def match(self, xn):
        """Processes a transaction against this rule

        If all conditions are satisfied, a list of outcomes is returned.
        If any condition is unsatisifed, None is returned.
        """
        if all(map(lambda x: x.match(xn), self.conditions)):
            return self.outcomes
        return None
