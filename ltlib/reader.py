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

import csv


class ReadError(Exception):
    """Unable to read the file"""
    pass


class DataError(Exception):
    """Unexpected or malformed data in input file"""
    pass


class Reader(object):
    """Base class for transaction file readers

    A Reader is an iterator that takes a transaction file of some kind
    and provides transaction objects.
    """
    def __init__(self, **kwargs):
        super(Reader, self).__init__()

        if 'file' not in kwargs:
            raise ReadError("No file provided")
        self.file = kwargs['file']

    def __iter__(self):
        """Return an iterator for the Reader"""
        raise NotImplementedError

    def next(self):
        """Return the next item.

        Must raise StopIteration when the file has no more transactions
        """
        raise NotImplementedError


class CsvReader(Reader):
    """Base class for CSV file readers

    Uses csv.DictReader and assumes the field names are provided as the
    first line of the csv.  TODO: make this frobbable.
    """
    def __init__(self, **kwargs):
        super(CsvReader, self).__init__(**kwargs)
        self.csvreader = csv.DictReader(self.file)

    def dict2xn(self, d):
        raise NotImplementedError

    def __iter__(self):
        return self

    def next(self):
        """Return the next transaction object.

        StopIteration will be propagated from self.csvreader.next()
        """
        return self.dict2xn(self.csvreader.next())
