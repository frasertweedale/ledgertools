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

import re


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

    def __repr__(self):
        return "{}(value={!r})".format(self.__class__.__name__, self.value)


class OperatorCondition(Condition):
    def __init__(self, *args, **kwargs):
        self.op = kwargs.pop('op')
        super(OperatorCondition, self).__init__(*args, **kwargs)


class AccountCondition(Condition):
    def __init__(self, *args, **kwargs):
        """
        Any '::' expands to 1+ intermediate fragments.
        No ':' at start anchors fragment at beginning.
        No ':' at end anchors fragment at end.
        """
        super(AccountCondition, self).__init__(*args, **kwargs)
        pattern = self.value.replace('::', ':[\w ]+(?::[\w ]+)*:')
        if pattern[0] != ':':
            pattern = '^' + pattern
        if pattern[-1] != ':':
            pattern = pattern + '$'
        self.re = re.compile(pattern)


class SourceCondition(AccountCondition):
    def match(self, xn):
        if xn.src is None:
            return False
        return filter(lambda src: self.re.search(src.account), xn.src)


class DestinationCondition(AccountCondition):
    def match(self, xn):
        if xn.dst is None:
            return False
        return filter(lambda dst: self.re.search(dst.account), xn.dst)


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


class DropOutcome(Outcome):
    def __init__(self, *args, **kwargs):
        super(DropOutcome, self).__init__(*args, value=None, **kwargs)


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
