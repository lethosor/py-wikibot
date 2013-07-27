"""
Users
"""

import api

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
        
        if username and password and auto_login:
            self.login()
    
    def login(self, username='', password=''):
        val_1 = self.api.request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password
        }, ret='value', filters=['login'])
        # if val_1['result'] == 'NeedToken':
        print val_1
        req_2 = self.api.request({
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': val_1['token']
        }, ret='request')
        print req_2
        
    
    

