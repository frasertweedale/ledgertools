from __future__ import division

import math


def number(items):
    """Maps numbering onto given values"""
    n = len(items)
    if n == 0:
        return items
    places = str(int(math.log10(n) // 1 + 1))
    format = '[{0[0]:' + str(int(places)) + 'd}] {0[1]}'
    return map(
        lambda x: format.format(x),
        enumerate(items)
    )


def filter_yn(string, default=None):
    """Return True if yes, False if no, the boolean default or None."""
    if string.startswith(('Y', 'y')):
        return True
    elif string.startswith(('N', 'n')):
        return False
    elif not string and (default is True or default is False):
        return default
    return None


def filter_int(string, default=None):
    """Return the input integer, the default, or None on error"""
    try:
        return int(string)
    except ValueError:
        return default if string == '' else None


class UI(object):
    def show(self, msg):
        print msg

    def yn(self, prompt, default=None):
        """Prompts the user for yes/no confirmation, with optional default"""
        if default is True:
            opts = " [Y/n]: "
        elif default is False:
            opts = " [y/N]: "
        else:
            opts = " [y/n]: "
        prompt += opts
        response = None
        while response is None:
            response = filter_yn(raw_input(prompt), default)
        return response

    def choose(self, items, default=None):
        """Prompts the user to choose one item from a list"""
        if default is not None and (default >= len(items) or default < 0):
            raise IndexError  # TODO raise a more sensible exception
        self.show("\n".join(number(items)))  # show the items
        prompt = "Enter number of chosen item"
        prompt += " [{0:d}]: ".format(default) if default is not None else ': '
        response = None
        while response is None:
            response = filter_int(raw_input(prompt), default)
            if response is not None:
                try:
                    return items[response]
                except IndexError:
                    response = None
                    print "value out of range"
