from distutils.core import setup

setup(
    name='ledgertools',
    version='0.1dev',
    description='Utilities for the Ledger accounting system',
    author='Fraser Tweedale',
    author_email='frase@frase.id.au',
    url='http://frase.id.au/repo/ledgertools.git',
    packages=['ltlib', 'ltlib.readers', 'ltlib.test'],
    scripts=['bin/lt-stmtproc', 'bin/lt-transact'],
)
