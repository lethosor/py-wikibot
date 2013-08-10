"""
template_subst

Replaces all occurences of a template with the substituted template
"""

import re

import wikibot
import wikibot.bot as bot

class TemplateSubstTask(bot.Task):
    def __init__(self, user, template_name, summary='Substituting {template_name} ({0}/{1})'):
        super(TemplateSubstTask, self).__init__(user, TemplateSubstJob)
        if ':' in template_name:
            template_ns, template_name = template_name.split(':', 1)
        template_name = template_ns + ':' + template_name
        self.page_names_query = {
            'list': 'embeddedin',
            'eititle': template_name,
            'eilimit': 500
        }
        
        self.user, self.template_name, self.template_ns, self.summary = \
            user, template_name, template_ns, summary
        
        if template_ns.lower() == 'template':
            name = template_name.split(':', 1)[1]
            t_regex = '{{([Tt][Ee][Mm][Pp][Ll][Aa][Tt][Ee]:)?%s([|}])' % name
            replacement = "{{subst:%s" % name
        else:
            name = template_name
            t_regex = '{{(%s)([|}])' % template_name
            t_replacement = "{{subst:%s" % template_name
        
        self.t_regex, self.t_replacement = t_regex, t_replacement
        self.template = name
        
class TemplateSubstJob(bot.Job):
    def run(self):
        self.page.text = re.sub(self.task.t_regex, self.task.t_replacement + r'\2', self.page.text)
        return True
    
    def save(self):
        self.page.save(
            summary=self.task.summary.format(*self.count, template_name=self.task.template),
            bot=1
        )

def run():
    user = wikibot.cred.get_user()
    args = wikibot.command_line.parse_args()
    template = args['template'] if 'template' in args else wikibot.util.input('Template: ')
    
    task = TemplateSubstTask(user, template)
    task.run_all()

if __name__ == '__main__':
    run()
