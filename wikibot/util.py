"""
Utilities
"""

# Consistency
from __future__ import print_function

import sys
import urllib

py_version = int(sys.version.split()[0].split('.')[0])

def log(*args):
    print(' '.join([str(x) for x in args]))

def die(*args):
    log(*args)
    sys.exit()

def dict_extend(d1, d2):
    return dict(d1, **d2)

def qs_decode(s):
    d = {}
    a = s.split('&')
    for i in a:
        b = i.split('=',1)
        d[urllib.unquote(b[0])] = urllib.unquote(b[1])
    return d
    
def qs_encode(d):
    data_string = ''
    for i in d:
        data_string += "&%s=%s" % (urllib.quote(i), urllib.quote(d[i]))
    
    data_string = data_string[1:]
    return data_string
