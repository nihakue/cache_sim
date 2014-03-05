import os

def trace_read(filename):
    basedir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(basedir, filename)
    try:
        return _get_trace(filepath)
    except IOError:
        while filepath != '/' + filename:
            parent_dir = os.path.dirname(os.path.dirname(filepath))
            filepath = os.path.join(parent_dir, filename)
            if os.path.exists(filepath):
                return _get_trace(filepath)
        else:
            raise IOError("Could not find file: %s" % filename)


def _get_trace(filepath):
    with open(filepath) as f_in:
        return [tuple(line.split()) for line in f_in.readlines()]
