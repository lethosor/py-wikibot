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
    
class Page:
    def __init__(self, title='', user=None, auto_load=True):
        self.title = title
        if user is None or not hasattr(user, 'api'):
            raise TypeError("Must have a valid user!")
        if auto_load:
            self.load()
    
    def load(self):
        pass
    
    


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
    def __init__(self, api, data={}, method='auto', auto=True, auto_filter=True, headers=None):
        data = util.dict_extend({'format':'json', 'action':'query'}, data)
           
        self.api, self.data, self.method, self.enable_auto_filter, self.headers = \
            api, data, method, auto_filter, headers
        
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
        self.req = req = network.Request(self.url_string, method=self.method, headers=self.headers)
        self.result = result = APIResult(self, req, self.data)
        return self.result
    
    def auto_filter(self, obj):
        while True:
            try:
                if len(obj.keys()) > 1:
                    break
                if isinstance(obj[obj.keys()[0]], dict):
                    obj = obj[obj.keys()[0]]
                else:
                    break
            except AttributeError:
                # Single remaining object is not a dict
                break
        
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
        self.headers = request.response.getheaders()
        if 'format' in data and data['format'] == 'json':
            self.value = json.loads(self.response)
            if api_request.enable_auto_filter:
                self.value = api_request.auto_filter(self.value)
    

