ledgertools is a collection of utility programs for working with and
visualising data in the Ledger_ accounting system.

``lt-stmtproc``
  Convert a bank statement into transactions in a Ledger database.

``lt-transact``
  Command line program for entering transactions.

``lt-chart``
  Visualise income or expenditure as a multi-level pie chart.
  Requires Ledger_, PyGTK_ (2.12 or higher) and gtkchartlib_.

.. _Ledger: https://github.com/jwiegley/ledger
.. _PyGTK: http://www.pygtk.org/
.. _gtkchartlib: http://pypi.python.org/pypi/gtkchartlib


Installation
------------

::

    pip install ledgertools


License
-------

ledgertools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.


Contributing
------------

The ledgertools source code is available from
https://github.com/frasertweedale/ledgertools.

Bug reports, patches, feature requests, code review and
documentation are welcomed.

To submit a patch, please use ``git send-email`` or generate a pull
request.  Write a `well formed commit message`_.  If your patch is
nontrivial, update the copyright notice at the top of each changed
file.

.. _well formed commit message: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
