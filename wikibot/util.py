"""
Utilities
"""

# Consistency
from __future__ import print_function

import copy
import getpass
import re
import readline
import sys

py_version = sys.version_info.major

if py_version == 2:
    import urllib
else:
    import urllib.parse as urllib

try:
    import termcolor
    if sys.platform == 'win32':
        # Only enable termcolor on Windows if colorama is available
        try:
            import colorama
            colorama.init()
        except ImportError:
            colorama = termcolor = None
except ImportError:
    termcolor = None
if not sys.stdout.isatty() or '--no-color' in sys.argv:
    # Prevent coloring of output with  --no-color or if stdout is not a tty
    termcolor = None


class DynamicList(list):
    def __setitem__(self, i, v):
        # Fill with None
        self[len(self):i+1] = [None for x in range(i+1-len(self))]
        super(DynamicList, self).__setitem__(i, v)

_log_color_split = re.compile('\s*[,/]?\s*')
_log_opts = re.compile('<[^>]*>')
_log_types = {
    'error': 'red, bold',
    'fatal': 'white, on_red, bold',
    'warn': 'yellow, bold',
    'ok': 'green',
    'success': 'green, bold',
    'info': 'blue',
    'progress': 'cyan',
    'bold': 'bold',
    'underline': 'underline',
}
def _log_parse(*args, **kwargs):
    s = ' '.join([str(x) for x in args]) + '<>'
    if 'type' in kwargs and kwargs['type'] in _log_types:
        s = '<' + _log_types[kwargs['type']] + '>' + s
    if 'color' not in kwargs:
        kwargs['color'] = True
    if termcolor is not None and kwargs['color']:
        parts = s.replace('\01', '').replace('<', '\01<').split('\01')
        s = ''
        for p in parts:
            if '>' in p:
                opts, text = p.split('>', 1)
                if opts[1:2] == '+':
                    opts = opts[2:]
                else:
                    opts = opts[1:]
                    s += termcolor.RESET
                opts = _log_color_split.split(opts)
                args, attrs = [None, None], []
                for opt in opts:
                    opt = opt.lower()
                    if opt in termcolor.COLORS:
                        args[0] = opt
                    elif opt in termcolor.HIGHLIGHTS:
                        args[1] = opt
                    elif opt in termcolor.ATTRIBUTES:
                        attrs.append(opt)
                s += termcolor.colored(text, *args, **{'attrs': attrs}).replace(termcolor.RESET, '')
            else:
                s += p
    else:
        # Remove <...> tags if termcolor isn't available
        s = _log_opts.sub('', s)
    return s

def log(*args, **kwargs):
    print(_log_parse(*args, **kwargs))

def logf(*args, **kwargs):
    sys.stdout.write(_log_parse(*args, **kwargs))
    sys.stdout.flush()

_debug = ('--debug' in sys.argv)
def debug(*args, **kwargs):
    if _debug:
        return log(*args, **kwargs)

_input = input if py_version == 3 else raw_input

def input(prompt='', visible=True, input=''):
    """
    Enhanced implementation of input (independent of Python version)
    Similar to Python 2's "raw_input" and Python 3's "input"

    prompt (string): The prompt to display (on the same line as the text)
    visible (bool): Enables/disables echoing of input. Note that "False"
        enforces a tty (i.e. it will read from the command line, not a file).
    input (string): Formatting to apply to the input string (only when visible)
        e.g. "red, bold" (angle brackets are not required)
    """
    prompt = _log_parse(prompt)
    if input and termcolor is not None:
        input = input.replace('<', '').replace('>', '')
        input = _log_parse('<%s>' % input).replace(termcolor.RESET, '')
    try:
        if not visible:
            text = getpass.getpass(prompt)
        else:
            text = _input(prompt + input)
    except:
        logf('<>')  # Reset terminal
        raise  # Allow exception to propagate
    logf('<>')
    return text

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

def die(*args, **kwargs):
    log(*args, **kwargs)
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
    """
    Merges dictionaries 'd1' and 'd2'
    For keys that exist in both, the value from d2 is used
    """
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


def qs_decode(string):
    data = {}
    a = string.split('&')
    if py_version == 2:
        for i in a:
            b = i.split('=',1)
            data[urllib.unquote(b[0]).decode('utf-8')] = urllib.unquote(b[1]).decode('utf-8')
    elif py_version == 3:
        for i in a:
            b = i.split('=',1)
            data[urllib.unquote(b[0])] = urllib.unquote(b[1])
    return data
    
def qs_encode(data):
    string = ''
    if py_version == 2:
        for i in data:
            string += "&%s=%s" % (urllib.quote(i).encode('utf-8'),
                                  urllib.quote(unicode(data[i]).encode('utf-8')))
    elif py_version == 3:
        for i in data:
            string += "&%s=%s" % (urllib.quote(i), urllib.quote(str(data[i])))
    string = string[1:]
    return string
