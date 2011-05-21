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


def value(item):
    return item[0]


def score(item):
    return item[1]


class ScoreSet(object):
    def __init__(self, items=None, **kwargs):
        self.items = items or {}

    def __contains__(self, item):
        key = item[0] if isinstance(item, tuple) else item
        return key in self.items

    def append(self, item):
        """Append an item to the score set.

        item is a pair tuple, the first element of which is a valid dict
        key and the second of which is a numeric value.
        """
        if item in self:
            self.items[item[0]].append(item[1])
        else:
            self.items[item[0]] = [item[1]]

    def scores(self):
        """Return a list of the items with their final scores.

        The final score of each item is its average score multiplied by the
        square root of its length.  This reduces to sum * len^(-1/2).
        """
        return map(
            lambda x: (x[0], sum(x[1]) * len(x[1]) ** -.5),
            iter(self.items.viewitems())
        )

    def highest(self):
        """Return the items with the higest score.

        If this ScoreSet is empty, returns None.
        """
        scores = self.scores()
        if not scores:
            return None
        maxscore = max(map(score, scores))
        return filter(lambda x: score(x) == maxscore, scores)
