""" API """

import wikibot
import wikibot.wikitools as wikitools

class Site(wikitools.wiki.Wiki):
    def __init__(self, url):
        if isinstance(url, self.__class__):
            # Allow passing a Site instance
            url = url.url
        if url.endswith('.php'):
            url = url.rsplit('/', 1)[0]
        if url.endswith('/'):
            url = url[:-1]
        url += "/api.php"
        wikitools.wiki.Wiki.__init__(self, url)
Wiki = Site

class Page(wikitools.page.Page):
    @property
    def text(self):
        return self.getWikiText()
    @text.setter
    def text(self, text):
        self._wikitext = text
    def save(self, *args, **kwargs):
        if hasattr(self, '_wikitext'):
            if self._wikitext != self.getWikiText():
                kwargs['text'] = self._wikitext
        self.edit(*args, **kwargs)
