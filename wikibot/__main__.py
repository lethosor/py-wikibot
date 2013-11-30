"""
Helper script, run with "python -m wikibot"
"""
import sys, wikibot
util = wikibot.util
if __name__ == '__main__':
    util.log("""\
<bold, red>Error: <red>The "wikibot" module cannot be run standalone.<>
You may be looking for:
*   <bold>python -m wikibot.console<>, an interactive wikibot command line
*   <bold>python -m wikibot.new_user<>, a script to create a new user
*   <bold>python -m wikibot.cred<>, which provides information about user credentials\
""")
    try:
        ans = util.input('Would you like to start an interactive console? (<bold>y<>/n) ')
        if ans.lower() != 'n':
            import wikibot.console
            wikibot.console.main()
    except:
        # Quit without a traceback
        util.log()