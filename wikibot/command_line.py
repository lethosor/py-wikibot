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
    """.replace('  ', '')
    args = parse_args()
    if 'user' in args:
        return wikibot.cred.load_user(args['user'])
    else:
        while 1:
            ident = wikibot.util.input('User ID (site:username), "?" for help: ')
            if ident == 'a':
                return
            elif ident == 'o':
                return get_user_creds()
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

def get_user_creds():
    util.log('Press Ctrl-C to abort user creation.')
    try:
        while 1:
            url = util.input('Wiki URL: ')
            try:
                api = wikibot.api.API(url)
            except wikibot.api.ApiInvalidResponseError:
                util.log('Invalid URL - use the "script path" URL found at Special:Version on your wiki.')
            except:
                util.log('An error occured while connecting to the server. Please check the URL.')
            else:
                break
        while 1:
            username = util.input('Username: ')
            password = util.input('Password: ', visible=False)
            user = wikibot.user.User(url, username, password)
            if user.logged_in:
                break
            util.log('Incorrect username/password. Please try again.')
        util.log('''
        Choose a unique identifier for this site (for example, "enwiki" would be
        appropriate for the English Wikipedia).'''.replace('  ', ''))
        while 1:
            ident = util.input('Identifier: ')
            if ':' in ident:
                util.log('Colons are not allowed in site identifiers.')
            elif not ident:
                pass
            else:
                break
        ident = ident + ':' + username
        util.log('Creating user %s...' % ident)
    except KeyboardInterrupt:
        util.log('\nUser creation aborted.')
    
    return {
        'site_url': url,
        'username': username,
        'password': password,
        'identifier': ident
    }
    
def create_new_user():
    util.log('Creating new user')
    user_info = get_user_creds()
    