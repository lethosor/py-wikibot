"""
Network connections
"""

__metaclass__ = type

import multiprocessing
import sys

import wikibot.util as util

if util.py_version == 2:
    from httplib import HTTPConnection
    from urlparse import urlparse
elif util.py_version == 3:
    from http.client import HTTPConnection
    from urllib.parse import urlparse
else:
    raise util.UnsupportedPythonVersion()

class Request:
    def __init__(self, url, data=False, method="GET", headers=False, auto=True):
        if not data:
            data = {}
        if not headers:
            headers = []
        purl = urlparse(url)  # Parsed URL
        if purl.query:
            data.update(util.qs_decode(purl.query.lstrip('?')))
        
        self.host, self.port, self.path, self.data, self.method, self.headers = \
            purl.hostname, purl.port, purl.path, data, method, headers
        
        if auto:
            self.request()
    
    def request(self):
        self.conn = HTTPConnection(self.host, self.port)
        query = util.qs_encode(self.data)
        self.post_data = ''
        if self.method == 'POST':
            self.post_data = query
            self.headers.append(("Content-type", "application/x-www-form-urlencoded"))
        elif self.method == 'GET':
            self.path += '?' + query
        else:
            raise ValueError('Invalid method: "%s"' % self.method)
        
        return self.fetch()

    def fetch(self):
        self.conn.putrequest(self.method, self.path)
        self.headers.append(('Content-Length', len(self.post_data)))
        sent_headers = []
        # Make sure we don't accidentally send duplicate headers
        for i in self.headers:
            header, value = i
            if header in sent_headers:
                # Don't send a header that's been sent already
                continue
            sent_headers.append(header)
            self.conn.putheader(header, value)
        self.conn.endheaders()
        # encode() converts data to bytes, needed for Python 3
        self.conn.send(self.post_data.encode())
        self.response = self.conn.getresponse()
        self.response_text = self.response.read()
    
    
class CookieManager:
    def __init__(self):
        self.cookies = {}
    
    def __getitem__(self, key):
        if key in self.cookies:
            return self.cookies[key]
        else:
            raise KeyError('No cookie found with name "%s"' % key)
    
    def __setitem__(self, key, val):
        self.cookies[key] = val
        return val
    
    get = __getitem__
    set = __setitem__
    
    def get_headers(self):
        """
        Returns a list containing a Cookie header for sending cookies, suitable
        for httplib requests (the list makes appending other headers easier).
        List format: [('Cookie', 'name=value; name=value ...')]
        The Cookie header can be created with:
        ': '.join(get_headers()[0])
        """
        cookies = []
        for c in self.cookies:
            cookies.append(util.qs_encode({c: self.cookies[c]}))
        return [("Cookie", "; ".join(cookies))]
    

    def set_from_headers(self, headers):
        """
        Sets cookies using all set-cookie headers in the given list.
        List format: [('set-cookie', 'cookie data')...]
        
        "Set-Cookie" is not case-sensitive. Other headers are ignored.
        """
        for h in headers:
            header, data = h
            if header.lower() != 'set-cookie':
                continue
            cookie_name, cookie_value = data.split(';')[0].split('=', 1)
            self.cookies[cookie_name] = cookie_value

