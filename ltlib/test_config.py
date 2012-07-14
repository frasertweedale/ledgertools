# This file is part of ledgertools
# Copyright (C) 2012 Fraser Tweedale
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
import unittest

from . import config


class FormatOutpatTestCase(unittest.TestCase):
    def setUp(self):
        class BogoXn(object):
            __slots__ = ['date']
        self.xn = BogoXn()
        self.xn.date = datetime.date(2012, 7, 1)

    def test_year(self):
        self.assertEqual(config.format_outpat('{year}', self.xn), '2012')

    def test_month(self):
        self.assertEqual(config.format_outpat('{month}', self.xn), '07')
        self.xn.date = datetime.date(2012, 12, 31)
        self.assertEqual(config.format_outpat('{month}', self.xn), '12')

    def test_fy(self):
        self.assertEqual(config.format_outpat('{fy}', self.xn), '2013')
        self.xn.date = datetime.date(2012, 6, 30)
        self.assertEqual(config.format_outpat('{fy}', self.xn), '2012')

    def test_date(self):
        self.assertEqual(
            config.format_outpat(
                '{date.year}{date.month:02}{date.day:02}',
                self.xn
            ),
            '20120701'
        )
