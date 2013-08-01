"""
Command-line tools
"""

import wikibot
util = wikibot.util

def parse_args(args):
    flags = {}
    for arg in args:
        # Check for leading --
        if not arg.startswith('--'):
            continue
        arg = arg[2:].lower()
        # Store in dictionary
        if not '=' in arg:
            flags[arg] = True
        else:
            k, v = arg.split('=', 1)
            flags[k] = v
    if 'login' in flags:
        if 'site' in flags:
            site = flags['site']
        else:
            site = util.input('Wiki URL: ')
        wikibot.defaults.site = wikibot.api.Site(site)
        username = util.input('Username: ')
        password = util.input('Password: ', 0)

    

