"""
Console
"""

import readline
import code

import wikibot

vars = globals().copy()
vars.update(locals())

args = wikibot.command_line.parse_args()
if 'user' in args or 'u' in args or 'login' in args:
    vars.update({'user': wikibot.cred.get_user()})
    wikibot.util.log("User available as 'user'")

shell = code.InteractiveConsole(vars)
shell.interact()
