"""
Users
"""

__metaclass__ = type

import api
import network
import util

class UserError(Exception):
    """
    A base exception class
    """
    pass

class UserLoginError(UserError):
    """
    An error while logging in a user
    """
    pass

class UserPermissionError(UserError):
    """
    Indicates a lack of sufficient privileges
    """
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
            api_obj = api.API(site)
        
        self.api = api_obj
        
        self.cookies = network.CookieManager()
        
        if username and password and auto_login:
            self.login()
    
    
    def login(self, username='', password='', auto_init=True):
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
            util.log("Login as %s successful" % self.username)
        else:
            util.log("Login as %s failed: %s" % (self.username, val_2['result']))
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
        util.log('User %s initialized successfully' % self.username)
    
    
    def api_request(self, *args, **kwargs):
        cookie_headers = self.cookies.get_headers()
        if 'headers' in kwargs:
            kwargs['headers'].extend(cookie_headers)
        else:
            kwargs['headers'] = cookie_headers
        old_ret = 'value'
        if 'ret' in kwargs:
            old_ret = kwargs['ret']
        kwargs['ret'] = 'request'
        req = self.api.request(*args, **kwargs)
        self.cookies.set_from_headers(req.result.headers)
        if old_ret == 'value':
            return req.result.value
        elif old_ret == 'result':
            return req.result
        return req
        
    def get_page(self, page_name, *args, **kwargs):
        return api.Page(page_name, self, *args,**kwargs)
    

