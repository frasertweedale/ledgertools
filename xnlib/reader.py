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
