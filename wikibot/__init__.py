"""
Python MediaWiki bot framework

"""

import sys

# Submodules
import wikibot.api
import wikibot.bot
import wikibot.command_line
import wikibot.cred
import wikibot.network
import wikibot.user
import wikibot.util

# Credentials
import wikibot.creds

def init():
    command_line.parse_args(sys.argv)

