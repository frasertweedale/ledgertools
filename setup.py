from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(
    name='ledgertools',
    version='0.1',
    description='Ledger accounting system utilities',
    author='Fraser Tweedale',
    author_email='frase@frase.id.au',
    url='http://frase.id.au/repo/ledgertools.git',
    packages=['ltlib', 'ltlib.readers', 'ltlib.test'],
    scripts=['bin/lt-stmtproc', 'bin/lt-transact'],
    data_files=[
        ('doc/ledgertools', ['doc/.ltconfig.sample']),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
    long_description=long_description,
)
