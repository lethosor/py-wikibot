"""
Python MediaWiki bot framework

"""

import sys

# Submodules
import api
import bot
import command_line
import cred
import network
import user
import util

# Credentials
import creds

def init():
    command_line.parse_args(sys.argv)

