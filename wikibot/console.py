"""
Console
"""

import readline
import code
import importlib

import wikibot
util = wikibot.util

def main():
    util.log('Starting interactive wikibot shell...', type='info')
    
    c_vars = {}  # Console variables
    modules = ['sys', 'os', 're', 'wikibot', 'termcolor']
    for m in dir(wikibot):
        if m not in modules and not m.startswith('__') and m != 'wikibot':
            modules.append('wikibot.' + m)
    
    args = wikibot.command_line.parse_args()
    if 'modules' in args:
        try:
            modules.extend(args['modules'].split(','))
        except Exception:
            util.log('Invalid --modules argument', type='error')
    
    user_exists = False
    if 'user' in args or 'u' in args or 'login' in args:
        try:
            util.logf('Logging in...\r', type='progress')
            user = wikibot.cred.get_user()
        except ImportError:
            wikibot.util.die('User credentials for "%s" not found' % args['user'],
                             type='error')
        except wikibot.user.UserError as e:
            wikibot.util.die('Failed to log in: %s' % e, type='fatal')
        user_exists = True
        c_vars.update({'user': user})
        wikibot.util.log("<bold>User available as 'user'")
    
    for m in modules:
        name = m.split('.')[-1]
        while name in c_vars:
            name += '_'
        try:
            c_vars[name] = importlib.import_module(m)
            if m.endswith(name):
                util.log('Imported module "%s"%s' % (m, ' as "%s"' % name if name != m else ''),
                         type='progress')
            else:
                util.log('Imported module "%s" as "%s": Scope conflict' % (m, name), type='warn')
        except (ImportError, ValueError, TypeError) as e:
            util.log('Failed to import module "%s": %s' % (m, str(e)), type='error')
    
    shell = code.InteractiveConsole(c_vars)
    try:
        shell.interact()
    except:
        # Script will end anyway
        pass
    
    if user_exists:
        if user.logged_in:
            user.logout()
        else:
            util.log('User already logged out.', type='info')

if __name__ == '__main__':
    main()
