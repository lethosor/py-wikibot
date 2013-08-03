"""
Credential storage/retrieval
"""

import wikibot

def load_user(identifier):
    try:
        site_name, user_name = identifier.split(':')
    except ValueError:
        raise ValueError('User identifier should be in format site:username')
    try:
        creds = __import__('wikibot.cred.{0}.{1}'.format(site_name, user_name))
    except ImportError:
        raise ImportError('Credentials for {0} not found'.format(identifier))
    user = wikibot.user.User(site_name, creds.username, creds.password)
    return user
