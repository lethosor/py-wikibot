"""
Utilities
"""

# Consistency
from __future__ import print_function

import sys

py_version = int(sys.version.split()[0].split('.')[0])

def log(*args):
    print(' '.join([str(x) for x in args]))

def die(*args):
    log(*args)
    sys.exit()

def dict_extend(d1, d2):
    return dict(d1, **d2)

