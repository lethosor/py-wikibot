"""
Credential storage/retrieval
"""

import argparse
import importlib
import os

import wikibot

get_user = wikibot.command_line.get_user

def load_user(identifier):
    try:
        site_name, user_name = identifier.split(':')
    except ValueError:
        raise ValueError('User identifier should be in format site:username')
    try:
        site_info = importlib.import_module('wikibot.creds.{0}.__siteinfo__'.format(site_name))
        creds = importlib.import_module('wikibot.creds.{0}.{1}'.format(site_name, user_name))
    except ImportError:
        raise ImportError('Credentials for {0} not found'.format(identifier))
    user = wikibot.user.User(site_info.url, creds.username, creds.password)
    return user

def get_creds_path(*args):
    return os.path.join(os.path.dirname(__file__), 'creds', *args)

def save_init_file(site_id):
    """ Creates an init file, if it doesn't already exist """
    init_path = get_creds_path(site_id, '__init__.py')
    try:
        os.mkdir(os.path.dirname(init_path))
    except OSError:
        pass
    # Create empty file
    init_file = open(init_path, 'w')
    init_file.close()

def save_site_file(site_id, url):
    string = """\
# Site info for {site}
url = "{url}"
""".format(url=url, site=site_id)
    save_init_file(site_id)
    si_path = get_creds_path(site_id, '__siteinfo__.py')
    si_file = open(si_path, 'w')
    si_file.write(string)
    si_file.close()

def save_user_file(site_id, username, password):
    string = """\
# Credentials for {site}:{user}
username = "{user}"
password = "{password}"
""".format(site=site_id, user=username, password=password)
    save_init_file(site_id)
    path = get_creds_path(site_id, username + '.py')
    f = open(path, 'w')
    f.write(string)
    f.close()

if __name__ == '__main__':
    util = wikibot.util
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', help='List users', required=False, action='store_true')
    parser.add_argument('-u', '--user', help='List a specific user', required=False)
    parser.add_argument('-t', '--test', '--login', help='Attempt a login', required=False,
                        action='store_true')
    args = parser.parse_args()
    if args.list:
        path = get_creds_path()
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))
                and not d.startswith('_')]
        util.log('<bold, green, underline>List of users:')
        for d in dirs:
            p = os.path.join(path, d)
            files = [f.replace('.py', '') for f in os.listdir(p)
                     if os.path.isfile(os.path.join(p, f)) and f.endswith('.py')
                     and not f.startswith('_')]
            site_info = importlib.import_module('wikibot.creds.{0}.__siteinfo__'.format(d))
            util.log('<bold>%s<> (<bold, blue, underline>%s<>)' % (d, site_info.url))
            for f in files:
                user_info = importlib.import_module('wikibot.creds.{0}.{1}'.format(d, f))
                username = ('<bold, green>' + user_info.username if hasattr(user_info, 'username')
                            else '<bold, red>Unknown user')
                util.log('*   User: %s<> (<bold>%s:%s<>)' % (username, d, f))
    if args.user:
        if not ':' in args.user:
            util.die('Invalid user id!', type='fatal')
        d, f = args.user.split(':')
        try:
            site_info = importlib.import_module('wikibot.creds.{0}.__siteinfo__'.format(d))
            user_info = importlib.import_module('wikibot.creds.{0}.{1}'.format(d, f))
        except ImportError:
            util.die('Credentials not found for ' + args.user, type='fatal')
        util.log('User: <bold, green>%s <>(<bold>%s<>)' % (f, args.user))
        util.log('    URL: <blue, underline>' + site_info.url)
        util.log('    Username: <bold>' + user_info.username)
        if args.test:
            util.logf('Attempting to log in...\r', type='progress')
            try:
                user = load_user(args.user)
            except Exception:
                util.log('Unable to log in as ' + args.user, type='error')
