"""
Interface for the MediaWiki API
"""

import json
import pickle

# wikibot
import network
import util

class Site:
    def __init__(self, url):
        if isinstance(url, self.__class__):
            # Allow passing a Site instance
            url = url.url
        if url.endswith('.php'):
            url = url.rsplit('/', 1)[0]
        if url.endswith('/'):
            url = url[:-1]
        url += "/api.php"
        self.url = url
    


class API:
    def __init__(self, url='', auto=True, save_file=None):
        
        self.mw_data = {}
        self.info = {}  # Shortcuts for commonly-used items in mw_data
        
        # Load a saved file
        if save_file is not None and hasattr(save_file, 'read'):
            self.init_from_file(save_file)
            return
        # Set up API url
        self.url = Site(url).url
        
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
        ret = 'value'
        if 'ret' in kwargs:
            ret = kwargs['ret']
            del kwargs['ret']
        r = APIRequest(self, *args, **kwargs)
        if ret=='value':
            return r.result.value
        elif ret=='result':
            return r.result
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
            if self.data['action'] == 'query':
                self.method = 'GET'
            else:
                self.method = 'POST'
        if not self.method in ('GET', 'POST'):
            raise ValueError('Method must be GET/POST')
        self.req = req = network.Request(self.url_string, method=self.method)
        self.result = result = APIResult(self, req, self.data)
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
        

class APIResult:
    def __init__(self, api_request, request, data):
        self.response = request.response_text
        self.value = self.response
        if 'format' in data and data['format'] == 'json':
            self.value = json.loads(self.response)
            self.value = api_request.apply_filters(self.value)
    

