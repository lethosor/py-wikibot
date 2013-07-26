"""
Interface for the MediaWiki API
"""

import json
import pickle

# wikibot
import network
import util

class API:
    def __init__(self, url='', auto=True, save_file=None):
        
        self.mw_data = {}
        self.info = {}  # Shortcuts for commonly-used items in mw_data
        
        # Load a saved file
        if save_file is not None and hasattr(save_file, 'read'):
            self.init_from_file(save_file)
            return
        # Set up API url
        if url.endswith('.php'):
            url = url.rsplit('/', 1)[0]
        if url.endswith('/'):
            url = url[:-1]
        url += "/api.php"
        self.url = url
        
        if auto:
            self.init()
    
    def init_from_file(self, f):
        self.load(f)
        self.info = {}
    
    def init(self):
        """
        Perform network initialization
        """
        self.mw_data.update(self.request({
            'meta':'siteinfo',
            'siprop':'general|namespaces|namespacealiases|statistics'
        }))
    
    def request(self, *args, **kwargs):
        r = APIRequest(self, *args, **kwargs)
        if hasattr(r, 'result'):
            return r.result
        else:
            return r
    
    def save(self, outfile):
        data = (self.url, self.mw_data)
        pickle.dump(data, outfile)
    
    def load(self, infile):
        data = pickle.load(infile)
        self.url, self.mw_data = data
    


class APIRequest:
    def __init__(self, api, data={}, method='auto', auto=True, default_filters=['query'], filters=[]):
        data = util.dict_extend({'format':'json', 'action':'query'}, data)
        
        filters.extend(default_filters)
        
        self.api, self.data, self.method, self.filters = api, data, method, filters
        
        if auto:
            self.request()
        
    def request(self):
        self.method = self.method.upper()
        if self.method == 'AUTO':
            self.method = 'GET'
        if not self.method in ('GET', 'POST'):
            raise ValueError('Method must be GET/POST')
        self.req = req = network.Request(self.url_string)
        result = req.response_text
        if self.data['format'] == 'json':
            self.result = self.apply_filters(json.loads(result))
        else:
            self.result = result
        return self.result
    
    def apply_filters(self, obj):
        def sub(obj):
            found = False
            for i in self.filters:
                if i in obj:
                    found = True
                    obj = obj[i]
            return (found, obj)
        
        c = True
        while c:
            c, obj = sub(obj)
        
        return obj
    
    
    @property
    def url_string(self):
        data_string = ''
        for i in self.data:
            data_string += "&%s=%s" % (i, self.data[i])
        
        data_string = data_string[1:]
        return "%s?%s" % (self.api.url, data_string)
        
    

