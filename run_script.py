"""
Runs a bot script
"""

import importlib
import sys

import wikibot

if len(sys.argv) < 2 or not sys.argv[1]:
    wikibot.util.die('Usage: python run_script.py script [--user=userid] [options]')

script = sys.argv[1]
try:
    module = importlib.import_module(script)
except ImportError:
    wikibot.util.die('Could not load script: ' + str(script))

user = wikibot.cred.get_user()

if 'run' in dir(module):
    module.run()
