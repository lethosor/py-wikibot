"""
Command-line tools
"""

import sys

import wikibot
util = wikibot.util

def parse_args(args=None):
    if args is None:
        args = sys.argv
    flags = {}
    for arg in args:
        # Check for leading --
        if not arg.startswith('--'):
            continue
        arg = arg[2:]
        # Store in dictionary
        if not '=' in arg:
            flags[arg] = True
        else:
            k, v = arg.split('=', 1)
            flags[k] = v
    return flags

def get_user():
    help_str = """\
a: Abort
o: One-time login (bypass saving)\
"""
    args = parse_args()
    if 'user' in args:
        return wikibot.cred.load_user(args['user'])
    else:
        while 1:
            ident = wikibot.util.input('User ID (site:username), "?" for help: ')
            if ident == 'a':
                return
            elif ident == 'o':
                return get_one_time_user()
            elif ident == '?':
                # Create new user
                print help_str
            else:
                try:
                    return wikibot.cred.load_user(ident)
                except ImportError:
                    util.log('Could not load user data for {0}.'.format(ident))
                except ValueError:
                    util.log('"{0}" is not a valid user ID!'.format(ident))

def get_one_time_user():
    pass
    

