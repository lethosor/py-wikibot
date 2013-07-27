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
        req_1 = self.api.request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password
        }, ret='request', filters=['login'])
        self.cookies.set_from_headers(req_1.result.headers)
        val_1 = req_1.result.value
        req_2 = self.api.request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': val_1['token']
        }, ret='request', filters=['login'], headers=self.cookies.get_headers())
        val_2 = req_2.result.value
        if val_2['result'] == 'Success':
            util.log("Login as %s successful" % self.username)
        else:
            util.log("Login as %s failed: %s" % (self.username, val_2['result']))
    
    def api_request(self, *args, **kwargs):
        cookie_headers = self.cookies.get_headers()
        if 'headers' in kwargs:
            kwargs['headers'].extend(cookie_headers)
        else:
            kwargs['headers'] = cookie_headers
        return self.api.request(*args, **kwargs)
    

