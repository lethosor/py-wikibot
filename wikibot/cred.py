"""
Credential storage/retrieval
"""

import importlib

import wikibot

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

def save_site_file(identifier, url):
    string = """\
# Site info for {identifier}
url = {url}
""".format(url=url, identifier=identifier)

def save_user_file(site_id, username, password):
    string = """\
# Credentials for {site}:{user}
username = {user}
password = {password}
""".format(site=site_id, user=username, password=password)

