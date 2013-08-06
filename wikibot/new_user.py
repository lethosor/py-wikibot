"""
Simple script for creating a new user

Intended to be run as:
python -m wikibot.new_user
"""

import wikibot

if __name__ == '__main__':
    try:
        wikibot.command_line.create_new_user()
    except:
        wikibot.util.log('\nUser creation failed.')
