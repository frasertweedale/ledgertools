import unittest

import os

import ltlib.config

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
        self.config = ltlib.config.Config(text=text)

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
