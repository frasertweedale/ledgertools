def filter_yn(string, default=None):
    """Return True if yes, False if no, the boolean default or None."""
    if string.startswith(('Y', 'y')):
        return True
    elif string.startswith(('N', 'n')):
        return False
    elif not string and (default is True or default is False):
        return default
    return None


class UI(object):
    def show(self, msg):
        print msg

    def input(self, constructor, prompt):
        """Reads user input and returns an object

        The constructor take a single string and return an object.
        """
        return constructor(raw_input(prompt))

    def input_confirm(self, prompt, default=None):
        """Prompts the user for yes/no confirmation, with optional default"""
        if default is True:
            opts = " [Y/n]"
        elif default is False:
            opts = " [y/N]"
        else:
            opts = " [y/n]"
        prompt += opts
        contructor = functools.partial(filter_yn, default=default)
        response = None
        while response is None:
            response = input(constructor, prompt)
