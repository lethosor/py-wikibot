"""
Users
"""

__metaclass__ = type

import wikibot.api as api
import wikibot.network as network
import wikibot.util as util

class UserError(Exception):
    """ Base exception class """
    def __init__(self, *args):
        super(UserError, self).__init__(*args)
        util.log(*args, type='error')

class UserLoginError(UserError):
    """ An error while logging in a user """
    pass

class UserPermissionError(UserError):
    """ Indicates a lack of sufficient privileges """
    pass

class User:
    def __init__(self, site, username='', password='', auto_login=True, api_obj=None):
        self.logged_in = False
        if isinstance(site, str):
            site = api.Site(site)
        if not isinstance(site, api.Site):
            raise TypeError('Site must be an api.Site instance')
        
        self.site, self.username, self.password = site, username, password
        
        if api_obj is None:
            try:
                api_obj = api.API(site)
                self.api = api_obj
            except api.ApiError as e:
                raise UserError('Could not initialize API: %s' % e)
        
        self.cookies = network.CookieManager()
        
        if username and password and auto_login:
            self.login()
    
    
    def login(self, username='', password='', auto_init=True):
        try:
            req_1 = self.api_request({
                'action': 'login',
                'lgname': self.username,
                'lgpassword': self.password
            }, ret='request')
            val_1 = req_1.result.value
            req_2 = self.api_request({
                'action': 'login',
                'lgname': self.username,
                'lgpassword': self.password,
                'lgtoken': val_1['token']
            }, ret='request')
            val_2 = req_2.result.value
            if val_2['result'] == 'Success':
                util.log("Login as %s successful" % self.username, type="ok")
            else:
                raise UserLoginError("Login as %s failed: %s" % (self.username, val_2['result']), type="error")
                return False
        except api.ApiError as e:
            raise UserLoginError('Could not log in: %s' % e)
            return False
        
        self.logged_in = True
        # Set login cookies
        cookie_prefix = val_2['cookieprefix']
        self.cookies.set(cookie_prefix + 'UserID', val_2['lguserid'])
        self.cookies.set(cookie_prefix + 'UserName', self.username)
        self.cookies.set(cookie_prefix + 'Token', val_2['lgtoken'])
        
        if auto_init:
            self.init()
    
    def logout(self):
        self.api_request({'action':'logout'})
        util.log('Logged out %s' % self.username, type='info')
        self.logged_in = False
    
    def init(self):
        try:
            self.edit_token = self.api_request({
                'prop':'info',
                'intoken':'edit',
                'titles':'Main Page'
            })['edittoken']
        except Exception as e:
            raise UserError("Could not initialize user: %s" % e)
        util.log('User %s initialized successfully' % self.username, type="success")
    
    
    def api_request(self, *args, **kwargs):
        if len(args):
            try:
                a = args[0].copy()
                for k in a:
                    if 'password' in k:
                        a[k] = '<yellow>(Hidden)<blue>'
                util.debug('<blue>', str(a))
            except Exception:
                util.debug('<yellow>Query not displayed')
        cookie_headers = self.cookies.get_headers()
        if 'headers' in kwargs:
            kwargs['headers'].extend(cookie_headers)
        else:
            kwargs['headers'] = cookie_headers
        ret = 'value'
        if 'ret' in kwargs:
            ret = kwargs['ret']
        kwargs['ret'] = 'request'
        req = self.api.request(*args, **kwargs)
        self.cookies.set_from_headers(req.result.headers)
        if ret == 'value':
            r = req.result.value
        elif ret == 'result':
            r = req.result
        else:
            r = req
        util.debug(str(r), type='bold')
        return r
        
    def get_page(self, page_name, *args, **kwargs):
        return api.Page(page_name, self, *args,**kwargs)
    

