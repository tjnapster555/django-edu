VERSION = (0, 2, 'pre')

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    return '%s-%s' % (v, VERSION[-1])