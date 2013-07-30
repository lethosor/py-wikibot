"""
Bots
"""

__metaclass__ = type

import util

class Task:
    """
    A series of jobs
    """
    def __new__(cls, *args):
        if cls == Task:
            raise NotImplementedError("Tasks cannot be instantiated.")
        return super(Task, cls).__new__(cls, *args)
    
    def __init__(self, user, job, data):
        self.user, self.job, self.data = user, job, data
    
    def get_pages(self, ):
        page_names = []
        if hasattr(self, 'page_names'):
            page_names.extend(self.page_names)
        elif hasattr(self, 'page_names_query'):
            q = self.user.api_request(self.page_names_query)
            page_names.extend(util.dict_recursive_fetch_list(q['query'], 'title'))
        else:
            raise AttributeError("No list of page names found.")
        return page_names
    
    def run_job(self, page_name):
        page = self.user.get_page(page_name)
        data = None
        if page_name in self.data:
            data = self.data['page_name']
    
    
    

class Job:
    """
    An edit
    """
    def __init__(self, task, page, data, auto_run=True):
        if auto_run:
            self.run(task, page, data)
    

