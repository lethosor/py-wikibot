"""
Bots
"""

__metaclass__ = type

import time
import sys

import wikibot
import wikibot.util as util

class Task:
    """
    A series of jobs
    """
    def __new__(cls, *args, **kwargs):
        if cls == Task:
            raise NotImplementedError("Tasks cannot be instantiated.")
        return super(Task, cls).__new__(cls, *args, **kwargs)
    
    def __init__(self, user, job, data=None):
        if data is None:
            data = {}
        self.user, self.job, self.data = user, job, data
    
    def get_pages(self):
        page_names = []
        if hasattr(self, 'page_names'):
            page_names.extend(self.page_names)
        elif hasattr(self, 'page_names_query'):
            q = self.user.api_request(self.page_names_query, auto_filter=False)
            page_names.extend(util.dict_recursive_fetch_list(q['query'], 'title'))
        else:
            raise AttributeError("No list of page names found.")
        return page_names
    
    def run_job(self, page_name, count):
        page = self.user.get_page(page_name)
        data = None
        if page_name in self.data:
            data = self.data[page_name]
        job = self.job(self, page, data, count, auto_run=False)
        success = job.run()
        if success:
            job.save()
    
    def run_all(self):
        util.log("Starting jobs")
        start_time = time.time()
        pages = self.get_pages()
        self.progress_bar = wikibot.ui.ProgressBar(steps=len(pages), width=1000)
        count = [0, len(pages)]
        for page_name in pages:
            count[0] += 1
            self.run_job(page_name, count)
            self.progress_bar.inc()
        end_time = time.time()
        util.log("\nFinished")
    

class Job:
    """
    An edit
    """
    def __init__(self, task, page, data, count, auto_run=True):
        self.task, self.page, self.data, self.count = task, page, data, count
        if auto_run:
            self.run()
    
    def save(self):
        self.page.save()
    
    def format(self, string):
        return util.str_format(string, data=self.data, page=self.page, job=self)
    
    

