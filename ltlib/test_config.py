# This file is part of ledgertools
# Copyright (C) 2011, 2012 Fraser Tweedale
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
import os
import unittest

from . import config

text = r"""
{
    "rootdir": "~/ledger",
    "outdir": "General",
    "outpat": "out.dat",
    "rulesdir": "rules",
    "rules": [ "General.rules" ],

    "transact-default-account": "Expenses:Cash",

    "accounts": {
        "Assets:AccountA": {
        },
        "Assets:AccountB": {
            "transact-default-account": "Foo:Bar",
            "outdir": "AccountB",
            "outpat": "AccountB.dat",
            "rulesdir": "rules/AccountB",
            "rules": [ "AccountB.rules" ]
        }
    }
}
"""


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.config = config.Config(text=text)

    def test_get(self):
        # no account
        self.assertEqual(
            self.config.get('transact-default-account'),
            'Expenses:Cash'
        )
        # not overridden by account
        self.assertEqual(
            self.config.get(
                'transact-default-account',
                acc='Assets:AccountA'
            ),
            'Expenses:Cash'
        )
        # overriden by account
        self.assertEqual(
            self.config.get(
                'transact-default-account',
                acc='Assets:AccountB'
            ),
            'Foo:Bar'
        )
        # nonexistant config (no default)
        self.assertIsNone(self.config.get('fake'))
        # nonexistant config (use default)
        self.assertTrue(self.config.get('fake', acc=None, default=True))
        # nonexistant account (no default)
        self.assertIsNone(self.config.get('fake', acc='Foo'))
        # nonexistant account (use default)
        self.assertTrue(self.config.get('fake', acc='Foo', default=True))

    def test_rootdir(self):
        self.assertEqual(
            self.config.rootdir(),
            os.path.normpath(os.path.expanduser('~/ledger'))
        )

    def test_outdir(self):
        # no account
        self.assertEqual(
            self.config.outdir(),
            os.path.expanduser('~/ledger/General')
        )
        # not defined by account
        self.assertEqual(
            self.config.outdir('Assets:AccountA'),
            os.path.expanduser('~/ledger/General')
        )
        # defined by account
        self.assertEqual(
            self.config.outdir('Assets:AccountB'),
            os.path.expanduser('~/ledger/AccountB')
        )

    def test_outpat(self):
        # no account
        self.assertEqual(
            self.config.outpat(),
            os.path.expanduser('~/ledger/General/out.dat')
        )
        # not defined by account
        self.assertEqual(
            self.config.outpat('Assets:AccountA'),
            os.path.expanduser('~/ledger/General/out.dat')
        )
        # defined by account
        self.assertEqual(
            self.config.outpat('Assets:AccountB'),
            os.path.expanduser('~/ledger/AccountB/AccountB.dat')
        )

    def test_rulesdir(self):
        # no account
        self.assertEqual(
            self.config.rulesdir(),
            os.path.expanduser('~/ledger/rules')
        )
        # not defined by account
        self.assertEqual(
            self.config.rulesdir('Assets:AccountA'),
            os.path.expanduser('~/ledger/rules')
        )
        # defined by account
        self.assertEqual(
            self.config.rulesdir('Assets:AccountB'),
            os.path.expanduser('~/ledger/rules/AccountB')
        )

    def test_rulefiles(self):
        # no account
        self.assertSetEqual(
            set(self.config.rulefiles()),
            set([os.path.expanduser('~/ledger/rules/General.rules')])
        )
        # not defined by account
        self.assertSetEqual(
            set(self.config.rulefiles('Assets:AccountA')),
            set([os.path.expanduser('~/ledger/rules/General.rules')])
        )
        # defined by account
        self.assertSetEqual(
            set(self.config.rulefiles('Assets:AccountB')),
            set((
                os.path.expanduser('~/ledger/rules/' + x)
                for x in ['General.rules', 'AccountB/AccountB.rules']
            ))
        )

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
