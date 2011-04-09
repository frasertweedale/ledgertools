from distutils.core import setup

setup(
    name='xnproc',
    version='0.1dev',
    description='Rule-based transaction processing framework',
    author='Fraser Tweedale',
    author_email='frase@frase.id.au',
    url='http://frase.id.au/',
    packages=['xnlib', 'xnlib.readers', 'xnlib.test'],
    scripts=['bin/cash2ledger', 'bin/xn2ledger'],
)
