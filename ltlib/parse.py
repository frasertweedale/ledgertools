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

import datetime
import decimal
import functools
import operator
import re
import shlex

from . import rule


class Parser(object):
    def __init__(self):
        self.state = ConditionState()  # start in ConditionState

    def eatwords(self, words):
        if words[0] == 'then':
            words.pop(0)
            self.state = OutcomeState()  # switch to OutcomeState
        return self.state.eatwords(words)


class TypeState(object):
    def __init__(self, cls):
        self.cls = cls

    def eatwords(self, words):
        return functools.partial(self.cls, value=self.cast(words.pop(0)))


class NoneState(TypeState):
    def eatwords(self, words):
        return self.cls


class AccountState(TypeState):
    def cast(self, value):
        return value  # TODO cast to valid account


class AmountState(TypeState):
    def cast(self, value):
        return decimal.Decimal(value)


class DescriptionState(TypeState):
    def cast(self, value):
        return re.compile(value, re.IGNORECASE)


class DateState(TypeState):
    def cast(self, value):
        # TODO: cast to datetime.Date object
        date = None
        return date


class ConditionState(object):
    partial = functools.partial
    dispatch = {
        'from': AccountState(rule.SourceCondition),
        'to': AccountState(rule.DestinationCondition),
        'lt': AmountState(partial(rule.AmountCondition, op=operator.lt)),
        'le': AmountState(partial(rule.AmountCondition, op=operator.le)),
        'eq': AmountState(partial(rule.AmountCondition, op=operator.eq)),
        'ne': AmountState(partial(rule.AmountCondition, op=operator.ne)),
        'ge': AmountState(partial(rule.AmountCondition, op=operator.ge)),
        'gt': AmountState(partial(rule.AmountCondition, op=operator.gt)),
        'desc': DescriptionState(rule.DescriptionCondition),
        'before': DateState(partial(rule.DateCondition, op=operator.lt)),
        'notafter': DateState(partial(rule.DateCondition, op=operator.le)),
        'on': DateState(partial(rule.DateCondition, op=operator.eq)),
        'noton': DateState(partial(rule.DateCondition, op=operator.ne)),
        'notbefore': DateState(partial(rule.DateCondition, op=operator.ge)),
        'after': DateState(partial(rule.DateCondition, op=operator.gt))
    }

    def eatwords(self, words):
        word = words.pop(0)
        return self.dispatch[word].eatwords(words)()


class OutcomeState(object):
    partial = functools.partial
    dispatch = {
        'from': AccountState(rule.SourceOutcome),
        'to': AccountState(rule.DestinationOutcome),
        'desc': DescriptionState(rule.DescriptionOutcome),
        'drop': NoneState(rule.DropOutcome),
    }

    def eatwords(self, words):
        word = words.pop(0)
        cls = self.dispatch[word].eatwords(words)
        return cls(score=int(words.pop(0)))


def line2rule(line):
    parser = Parser()
    words = shlex.split(line)
    acc = []
    try:
        while words:
            acc.append(parser.eatwords(words))
        return rule.Rule(*acc)
    except:
        if words:
            print "error on line: '" + line + "' at '" + words[0]
        else:
            print "error on line: '" + line
        raise


def file2rules(file):
    # filter out comments
    stripcomments = functools.partial(re.compile('\s*(?:#.*|$)').sub, '')
    return map(line2rule, filter(lambda x: x, map(stripcomments, file)))
