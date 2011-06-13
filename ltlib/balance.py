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

import decimal
import itertools
import re

pattern = re.compile(r'([-\d\.]+)(\s+)(.*)')


def match_to_dict(match):
    """Convert a match object into a dict.

    Values are:
        indent: amount of indentation of this [sub]account
        parent: the parent dict (None)
        account_fragment: account name fragment
        balance: decimal.Decimal balance
        children: sub-accounts ([])
    """
    balance, indent, account_fragment = match.group(1, 2, 3)
    return {
        'balance': decimal.Decimal(balance),
        'indent': len(indent),
        'account_fragment': account_fragment,
        'parent': None,
        'children': [],
    }


def balance(output):
    """Convert `ledger balance` output into an hierarchical data structure."""
    lines = map(pattern.search, output.splitlines())

    stack = []
    top = []
    for item in map(match_to_dict, itertools.takewhile(lambda x: x, lines)):
        # pop items off stack while current item has indent <=
        while stack and item['indent'] <= stack[-1]['indent']:
            stack.pop()

        # check if this is a top-level item
        if not stack:
            stack.append(item)
            top.append(item)
        else:
            item['parent'] = stack[-1]
            stack[-1]['children'].append(item)
            stack.append(item)

    return top
