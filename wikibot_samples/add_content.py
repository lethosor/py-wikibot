"""
batch_create

Creates a list of pages, each with the specified text.
"""

import wikibot

class AddContentTask(wikibot.bot.Task):
    def __init__(self, user, pages, text, location='prepend', summary='Adding content ({0}/{1})', data=None):
        if data is None:
            data = {}
        if isinstance(location, str):
            location = location.lower()
        super(AddContentTask, self).__init__(user, AddContentJob, data)
        self.text, self.location, self.summary = text, location, summary
        if isinstance(pages, list):
            self.page_names = pages
        elif isinstance(pages, dict):
            self.page_name_query = pages
        else:
            raise TypeError("Invalid page list")
    
    

class AddContentJob(wikibot.bot.Job):
    def run(self):
        location = self.task.location
        if isinstance(location, str):
            new_text = self.task.text
            if location == 'prepend':    
                self.page.text = new_text + self.page.text
            elif location == 'append':
                self.page.text += new_text
            return True
        elif hasattr(location, '__call__'):
            self.page.text = location(self.page.text, self.data)
            return True
        return False
    
    def save(self):
        self.page.save(
            summary=self.task.summary.format(*self.count),
            bot=1
        )
    
