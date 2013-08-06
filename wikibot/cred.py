"""
Credential storage/retrieval
"""

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


def save_site_file(site_id, url):
    string = """\
# Site info for {site}
url = "{url}"
""".format(url=url, site=site_id)
    # Create an init file
    init_path = get_creds_path(site_id, '__init__.py')
    try:
        os.mkdir(os.path.dirname(init_path))
    except OSError:
        pass
    # Create empty file
    init_file = open(init_path, 'w')
    init_file.close()
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
    path = get_creds_path(site_id, username + '.py')
