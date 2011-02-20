import collections


def flatten(xs):
    for x in xs:
        if isinstance(x, collections.Iterable) \
            and not isinstance(x, basestring):
            for y in flatten(x):
                yield y
        else:
            yield x
