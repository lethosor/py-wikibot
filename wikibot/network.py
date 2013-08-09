"""
Network connections
"""

__metaclass__ = type

import multiprocessing
import sys

import wikibot.util as util

if util.py_version == 2:
    import httplib
    import urlparse
elif util.py_version == 3:
    import http.client as httplib
    import urllib.parse as urlparse
else:
    util.die('Unsupported python version:', util.py_version)

class Request:
    def __init__(self, url, data=False, method="GET", headers=False, auto=True, async=False, callback=None):
        if not data:
            data = {}
        if not headers:
            headers = []
        purl = urlparse.urlparse(url)  # Parsed URL
        if purl.query:
            data.update(util.qs_decode(purl.query.lstrip('?')))
        
        
        self.host, self.port, self.path, self.data, self.method, self.headers = \
            purl.hostname, purl.port, purl.path, data, method, headers
        
        self.async, self.callback = async, callback
        
        if async and callback is None:
            raise TypeError('Asynchronous requests require a callback!')
        
        if auto:
            self.request()
    
    def request(self):
        self.conn = httplib.HTTPConnection(self.host, self.port)
        query = util.qs_encode(self.data)
        self.post_data = ''
        if self.method == 'POST':
            self.post_data = query
            self.headers.append(("Content-type", "application/x-www-form-urlencoded"))
        elif self.method == 'GET':
            self.path += '?' + query
        else:
            raise ValueError('Invalid method: "%s"' % self.method)

        if not self.async:
            self.fetch()
        else:
            # Fetch the request asynchronously
            def fetch(*args):
                util.log("Fetching")
                self.fetch()
            p = multiprocessing.Pool(1)
            r = p.apply_async(fetch, [1], self.callback)
        
    def fetch(self):
        self.conn.putrequest(self.method, self.path)
        self.headers.append(('Content-Length', len(self.post_data)))
        for i in self.headers:
            try:
                header, value = i
                self.conn.putheader(header, value)
            except (TypeError, ValueError):
                pass
        self.conn.endheaders()
        self.conn.send(self.post_data)
        self.response = self.conn.getresponse()
        self.response_text = self.response.read()
        # Callback
        if hasattr(self.callback, '__call__'):
            self.callback(self)
    
    
class CookieManager:
    def __init__(self):
        self.cookies = {}
        self.get = self.__getitem__
        self.set = self.__setitem__
    
    def __getitem__(self, key):
        if key in self.cookies:
            return self.cookies[key]
        else:
            raise KeyError('No cookie found with name "%s"' & key)
    
    def __setitem__(self, key, val):
        self.cookies[key] = val
        return val
    
    def get_headers(self):
        """
        Returns a list containing a Cookie header for sending cookies, suitable
        for httplib requests (the list makes appending other headers easier).
        List format: [('Cookie', 'name=value; name=value ...')]
        The Cookie header can be created with:
        ': '.join(get_headers()[0])
        """
        l = []
        for i in self.cookies:
            l.append("%s=%s" % (i, self.cookies[i]))
        return [("Cookie", "; ".join(l))]
    

    def set_from_headers(self, l):
        """
        Sets cookies using all set-cookie headers in the given list.
        Other headers are ignored.
        List format: [('set-cookie', 'cookie data')...] (not case-sensitive)
        """
        
        for i in l:
            header, data = i
            if header.lower() != 'set-cookie':
                continue
            cookie_name, cookie_value = data.split(';')[0].split('=', 1)
            self.cookies[cookie_name] = cookie_value
        
        
    
    
    

