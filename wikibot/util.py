"""
Utilities
"""

# Consistency
from __future__ import print_function

import copy
import getpass
import re
import sys

py_version = sys.version_info.major

if py_version == 2:
    import urllib
else:
    import urllib.parse as urllib

class DynamicList(list):
    def __setitem__(self, i, v):
        # Fill with None
        self[len(self):i+1] = [None for x in range(i+1-len(self))]
        super(DynamicList, self).__setitem__(i, v)

def log(*args):
    print(' '.join([str(x) for x in args]))

def logf(*args):
    sys.stdout.write(' '.join([str(x) for x in args]))
    sys.stdout.flush()

def input(prompt='', visible=True):
    if not visible:
        return getpass.getpass(prompt)
    
    logf(prompt)
    if visible:
        return sys.stdin.readline().rstrip('\n')
    else:
        return getpass.getpass('')

def get_file(prompt='File: ', exists=True, path=''):
    """
    Prompt for a file
    
    prompt: Text to display (defaults to "File: ")
    exists: True if file should exist (defaults to True)
    path: An initial path to use, returned if acceptable (optional)
    """
    path = str(path)
    while 1:
        if not path:
            path = input(prompt)
        if exists:
            try:
                f = open(path)
            except IOError:
                pass
            else:
                break
        else:
            break
        path = ''
    return path

def die(*args):
    log(*args)
    sys.exit()

def dict_auto_filter(obj):
    while True:
        try:
            if len(obj.keys()) > 1:
                break
            # list() is necessary for python 3, where keys() doesn't return
            # a list that supports indexes
            if isinstance(obj[list(obj.keys())[0]], dict):
                obj = obj[list(obj.keys())[0]]
            else:
                break
        except AttributeError:
            # Single remaining object is not a dict
            break
    
    return obj


def dict_extend(d1, d2):
    return dict(d1, **d2)

def dict_recursive_fetch_list(d, key):
    """
    Returns a list of _all_ values in dict 'd' with key 'key'
    Also fetches items in lists
    """
    l = []
    
    if isinstance(d, list):
        for i in d:
            l.extend(dict_recursive_fetch_list(i, key))
        return l
    for i in d:
        if i == key:
            l.append(d[i])
        elif isinstance(d[i], (dict, list)):
            l.extend(dict_recursive_fetch_list(d[i], key))
            
    return l

def recursive_merge(d1, d2):
    """
    Merges two dictionaries and their sub-dictionaries and/or lists
    """
    d1, d2 = copy.copy(d1), copy.copy(d2)
    result = {} if isinstance(d1, dict) or isinstance(d2, dict) else []
    keys = (list(d1.keys()) if isinstance(d1, dict) else range(len(d1))) + \
           (list(d2.keys()) if isinstance(d2, dict) else range(len(d2)))
    # Remove duplicates
    keys = list(set(keys))
    if isinstance(result, dict):
        # Current object is a dict
        for k in keys:
            if k in d1 and k in d2:
                v1, v2 = d1[k], d2[k]
                if v1 != v2:
                    if isinstance(v1, (dict, list)) and isinstance(v2, (dict, list)):
                        # Values can be merged
                        result[k] = recursive_merge(v1, v2)
                    else:
                        # Values cannot be merged, so return the value from d1
                        result[k] = v1
                else:
                    # Values are equal, so merging is unnecessary
                    result[k] = v1
            else:
                # Key is either in d1 or d2
                result[k] = d1[k] if k in d1 else d2[k]
    else:
        # Current object is a list
        result = d1 + d2
    return result
    

def str_format(string, *args, **kwargs):
    """
    A slightly modified version of the native str.format(), using {% and %}
    instead of { and }
    
    >>> str_format('{a}', a=2)
    {a}
    >>> str_format('{%a%}', a=2)
    2
    >>> str_format('{% a %}', a=2)
    2
    """
    # Accept whitespace directly inside {% ... %} tags
    string = re.compile(r'\{%\s+').sub('{%', string)
    string = re.compile(r'\s+%\}').sub('%}', string)
    string = string.replace('{','{{').replace('}','}}') \
        .replace('{{%', '{').replace('%}}','}')
    return string.format(*args, **kwargs)


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
        data_string += "&%s=%s" % (urllib.quote(i), urllib.quote(str(d[i])))
    
    data_string = data_string[1:]
    return data_string
