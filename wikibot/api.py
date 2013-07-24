"""
Interface for the MediaWiki API
"""

import json

# wikibot
import network
import util

class API:
    def __init__(self, url, auto=True):
        # Set up API url
        if url.endswith('.php'):
            url = url.rsplit('/', 1)[0]
        if url.endswith('/'):
            url = url[:-1]
        url += "/api.php"
        self.url = url
        if auto:
            self.init()
    
    def init(self):
        """
        Perform network initialization
        """
        self.request({'meta':'siteinfo', 'siprop':'namespaces'})
    
    def request(self, *args, **kwargs):
        r = APIRequest(self, *args, **kwargs)
        if hasattr(r, 'result'):
            return r.result
        else:
            return r
    


class APIRequest:
    def __init__(self, api, data={}, method='auto', auto=True):
        data = util.dict_extend({'format':'json', 'action':'query'}, data)
        
        self.api, self.data, self.method = api, data, method
        
        if auto:
            self.request()
        
    def request(self):
        self.method = self.method.upper()
        if self.method == 'AUTO':
            self.method = 'GET'
        if not self.method in ('GET', 'POST'):
            raise ValueError('Method must be GET/POST')
        print self.url_string
        self.req = req = network.Request(self.url_string)
        result = req.response_text
        print result
        self.result = json.loads(result)
        return self.result
    
    @property
    def url_string(self):
        data_string = ''
        for i in self.data:
            data_string += "&%s=%s" % (i, self.data[i])
        
        data_string = data_string[1:]
        return "%s?%s" % (self.api.url, data_string)
        
    

