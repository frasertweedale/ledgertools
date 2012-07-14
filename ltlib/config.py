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

import json
import os
import StringIO


def apply(filter):
    """Manufacture decorator that filters return value with given function.

    ``filter``:
      Callable that takes a single parameter.
    """
    def decorator(callable):
        return lambda *args, **kwargs: filter(callable(*args, **kwargs))
    return decorator


def format_outpat(outpat, xn):
    """
    Format an outpat for the given transaction.

    Format the given output filename pattern.  The pattern should
    be a format string with any combination of the following named
    fields:

    ``year``
      The year of the transaction.
    ``month``
      The month of the transaction, with leading zero for
      single-digit months.
    ``fy``
      The financial year of the transaction (being the year in
      which the financial year of the transaction *ends*).
      A financial year runs from 1 July to 30 June.
    ``date``
      The date object itself.  The format string may specify
      any attribute of the date object, e.g. ``{date.day}``.
      This field is deprecated.
    """
    return outpat.format(
        year=str(xn.date.year),
        month='{:02}'.format(xn.date.month),
        fy=str(xn.date.year if xn.date.month < 7 else xn.date.year + 1),
        date=xn.date
    )


class Config(object):
    def __init__(self, path='~/.ltconfig', text=None):
        """Initialise a Config object.

        ``path``
          The path to the config file.  Defaults to ``'~/.ltconfig'``.
          User expansion is performed on the value.
        ``text``
          JSON string that will be used for configuration.  If supplied,
          takes precedence over ``path``.
        """
        if text is None:
            path = os.path.expanduser(path)
            if os.path.isfile(path):
                with open(path) as fh:
                    self.data = json.load(fh)
            else:
                self.data = {}  # file doesn't exist; empty config
        else:
            self.data = json.load(StringIO.StringIO(text))

    def get(self, name, acc=None, default=None):
        """Return the named config for the given account.

        If an account is given, first checks the account space for the name.
        If no account given, or if the name not found in the account space,
        look for the name in the global config space.  If still not found,
        return the default, if given, otherwise ``None``.
        """
        if acc in self.data['accounts'] and name in self.data['accounts'][acc]:
            return self.data['accounts'][acc][name]
        if name in self.data:
            return self.data[name]
        return default

    @apply(os.path.normpath)
    @apply(os.path.expanduser)
    def rootdir(self):
        return self.get('rootdir')

    @apply(os.path.normpath)
    def outdir(self, acc=None):
        """Return the outdir for the given account.

        Attempts to create the directory if it does not exist.
        """
        rootdir = self.rootdir()
        outdir = self.get('outdir', acc=acc)
        dir = os.path.join(rootdir, outdir) if rootdir and outdir else None
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def outpat(self, acc=None):
        """
        Determine the full outfile pattern for the given account.

        Return None if not specified.
        """
        outdir = self.outdir(acc)
        outpat = self.get('outpat', acc=acc)
        return os.path.join(outdir, outpat) if outdir and outpat else None

    @apply(os.path.normpath)
    def rulesdir(self, acc=None):
        """
        Determine the rulesdir for the given account.

        Return None if not specified.
        """
        rootdir = self.rootdir()
        rulesdir = self.get('rulesdir', acc=acc, default=[])
        return os.path.join(rootdir, rulesdir) \
            if rootdir and rulesdir else None

    def rulefiles(self, acc=None):
        """Return a list of rulefiles for the given account.

        Returns an empty list if none specified.
        """
        rulesdir = self.rulesdir(acc)
        rules = [os.path.join(rulesdir, x) for x in self.get('rules', acc, [])]
        if acc is not None:
            rules += self.rulefiles(acc=None)
        return rules
