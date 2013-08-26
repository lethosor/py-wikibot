"""
Interface for the MediaWiki API
"""

__metaclass__ = type

import json
import pickle

# wikibot
import wikibot
import wikibot.network as network
import wikibot.util as util

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

class PageError(Exception):
    pass

class PageSaveError(PageError):
    pass


class Page:
    default_items = ['raw']
    
    def __init__(self, title='', user=None, auto_load=True):
        self.title = title
        if user is None or not hasattr(user, 'api'):
            raise TypeError("Must have a valid user!")
        self.user = user
        self.data = {}
        if auto_load:
            self.load()
    
    def load(self, items=None):
        """
        Load page data
        
        items: Data to load about the page, either a string (for only one piece
        of data) or a list. Defaults to 'raw'.
        Each item is translated to a self.fetch_<item> call.
        """
        if items is None:
            items = self.default_items
        if isinstance(items, str):
            items = [items]
        for i in items:
            f = "fetch_" + i
            if hasattr(self, f):
                func = getattr(self, f)
                if hasattr(func, '__call__'):
                    self.data[i] = func()
    
    def fetch_raw(self):
        result = self.user.api_request({
            'titles': self.title,
            'indexpageids': 1,
            'prop': 'revisions',
            'rvprop': 'content',
            'rvlimit': 1
        }, auto_filter=False, query_continue=False)
        page_id = int(result['query']['pageids'][0])
        if page_id > 0:
            self.exists = True
            text = result['query']['pages'][result['query']['pageids'][0]]['revisions'][0]['*']
        else:
            # Page does not exist (negative ID)
            self.exists = False
            text = ''
        return {
            'result': result,
            'text': text
        }
    
    
    def save(self, summary='', minor=0, bot=0, title=None, refresh=False):
        if title is None:
            title = self.title
        try:
            text = self.data['raw']['text']
        except KeyError:
            raise PageSaveError("No text available to save!")
        data = {
            'action': 'edit',
            'title': title,
            'text': self.data['raw']['text'],
            'summary': summary,
            'token': self.user.edit_token
        }
        if minor:
            data['minor'] = 1
        if bot:
            data['bot'] = 1
        self.user.api_request(data)
        if refresh:
            self.load()
    
    def save_to(self, title, *args, **kwargs):
        self.save(title=title, *args, **kwargs)
    
    @property
    def text(self):
        return self.data['raw']['text']
    
    @text.setter
    def text(self, new):
        self.data['raw']['text'] = new
        return new
    
class Category(Page):
    default_items = ['raw', 'pages']
    
    def __init__(self, title, *args, **kwargs):
        if not title.startswith('Category:'):
            title = 'Category:' + title
        super(Category, self).__init__(title, *args, **kwargs)
    
    def fetch_pages(self):
        pass

    
class ApiError(Exception):
    pass

class ApiInvalidResponseError(ApiError):
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
    def __init__(self, api, data={}, method='auto', auto=True, auto_filter=True,
                 headers=None, query_continue=True):
        data = util.dict_extend({'format':'json', 'action':'query'}, data)
        if data['action'] == 'query' and 'continue' not in data and query_continue:
            data['continue'] = ''
        
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
        self.result = self.send_request()
        value = self.result.value
        data = self.data.copy()
        while 'continue' in value:
            data.update(value['continue'])
            result = self.send_request(data)
            value = util.recursive_merge(result.value, value)
            if not 'continue' in result.value:
                del value['continue']
                break
        if self.enable_auto_filter:
            value = util.dict_auto_filter(value)
        self.result.value = value
        return self.result
    
    def send_request(self, data=None):
        if data is None:
            data = self.data
        self.req = network.Request(self.api.url, data=data, method=self.method, headers=self.headers)
        return APIResult(self, self.req, self.data, auto_filter=False)
    
    

class APIResult:
    def __init__(self, api_request, request, data, auto_filter=True):
        self.response = request.response_text.decode()
        self.value = self.response
        self.headers = request.response.getheaders()
        if 'format' in data and data['format'] == 'json':
            try:
                self.value = json.loads(self.response)
            except ValueError:
                raise ApiInvalidResponseError('API did not return a JSON result.')
            if auto_filter:
                self.apply_filter()
    
    def apply_filter(self):
        self.value = util.dict_auto_filter(self.value)
    
