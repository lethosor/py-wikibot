"""
batch_create

Creates a list of pages, each with the specified text.
"""

from wikibot import bot

class BatchCreateTask(bot.Task):
    def __init__(self, user, page_list, text, summary='Creating page ({current}/{total})', data=None):
        if data is None:
            data = {}
        super(BatchCreateTask, self).__init__(user, BatchCreateJob, data)
        self.page_names = page_list
        
        self.summary = summary
    
    

class BatchCreateJob(bot.Job):
    def run(self, task, page, data):
        pass
    


