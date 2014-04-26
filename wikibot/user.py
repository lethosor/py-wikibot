""" User authentication """

import os, re
import ConfigParser

import wikibot

class User(object):
    def __init__(self, *args):
        if len(args) == 1:
            self.new_from_id(*args)
        elif len(args) == 3:
            self.new_from_creds(*args)
        else:
            raise TypeError('__init__ takes 1 or 3 arguments (%i given)' %
                            (len(args)))
    def new_from_id(self, user_id):
        creds = UserCredentials(user_id).load_creds()
        return self.new_from_creds(*creds)
    def new_from_creds(self, url, username, password):
        self.site = wikibot.api.Site(url)
        self.site.login(username, password)

class AnonymousUser(User):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], wikibot.api.Site):
            self.site = wikibot.api.Site(args[0])
        else:
            super(AnonymousUser, self).__init__(*args)

class CredentialError(Exception):
    pass

class UserCredentials(object):
    def __init__(self, user_id, path='~/.py-wikibot-creds'):
        user_id = re.sub(r'[^A-Za-z0-9_\-:]', '', user_id)
        parts = user_id.split(':')
        if len(parts) != 2:
            raise ValueError('user_id should be in format site:username')
        # Allow ~ expansion and relative paths
        path = os.path.abspath(os.path.expanduser(path))
        self.filename = os.path.join(path, parts[0]) + '.txt'
        self.user_id = user_id

    def config_parser(self):
        """
        Create the credential file if it doesn't exist and return a ConfigParser
        """
        try:
            os.makedirs(os.path.dirname(self.filename))
        except OSError as e:
            if e.errno == 17:
                # Already exists
                pass
            else:
                raise
        with open(self.filename, 'a'):
            # Create and touch
            os.utime(self.filename, None)
        parser = ConfigParser.ConfigParser()
        parser.optionxform = str  # Case-sensitive
        parser.read(self.filename)
        return parser

    def load_creds(self):
        """ Returns (url, username, password) """
        parser = self.config_parser()
        try:
            url = parser.get('site', 'url')
            username = self.user_id.split(':')[1]
            return (url, username, parser.get('creds', username))
        except ConfigParser.Error as e:
            raise CredentialError('Failed to load credentials for %s: %s' %
                                  (self.user_id, e))

    def save_creds(self, password, url=None):
        """ Takes a password and an optional site URL """
        parser = self.config_parser()
        for section in ('site', 'creds'):
            if not parser.has_section(section):
                parser.add_section(section)
        site, username = self.user_id.split(':')
        if url is None:
            try:
                url = parser.get('site', 'url')
            except ConfigParser.Error:
                raise ValueError('No URL available for %s' % site)
        parser.set('site', 'url', url)
        parser.set('creds', username, password)
        print(self.filename)
        with open(self.filename, 'w') as f:
            parser.write(f)
