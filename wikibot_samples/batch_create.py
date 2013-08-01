"""
batch_create

Creates a list of pages, each with the specified text.
"""

import wikibot

class BatchCreateTask(wikibot.bot.Task):
    def __init__(self, user, page_list, text, summary='Creating page ({0}/{1})', data=None):
        if data is None:
            data = {}
        super(BatchCreateTask, self).__init__(user, BatchCreateJob, data)
        self.text, self.summary = text, summary
        self.page_names = page_list
    
    

class BatchCreateJob(wikibot.bot.Job):
    def run(self):
        if self.page.text != "":
            return False
        self.page.text = self.format(self.task.text, self.data)
        return True
    
    def save(self):
        self.page.save(
            summary=self.task.summary.format(*self.count),
            bot=1
        )
    
if __name__ == '__main__':
    wikibot.init()
