"""
Users
"""

import api
import network
import util

class User:
    def __init__(self, site, username='', password='', auto_login=True, api_obj=None):
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
    
    def login(self, username='', password=''):
        req_1 = self.api_request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password
        }, ret='request', filters=['login'])
        val_1 = req_1.result.value
        req_2 = self.api_request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': val_1['token']
        }, ret='request', filters=['login'])
        val_2 = req_2.result.value
        if val_2['result'] == 'Success':
            util.log("Login as %s successful" % self.username)
        else:
            util.log("Login as %s failed: %s" % (self.username, val_2['result']))
            return False
    
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
        
    

