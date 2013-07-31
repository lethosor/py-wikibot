"""
template_subst

Replaces all occurences of a template with the substituted template

Does NOT support query-continue yet
"""

import re

from wikibot import util

def run(user, template_name, template_ns="Template"):
    template_name = template_ns + ':' + template_name
    if not user.logged_in:
        user.login()
        if not user.logged_in:
            return False
    trans = user.api_request({
        'list': 'embeddedin',
        'eititle': template_name,
        'eilimit': 500
    }, auto_filter=False)
    page_list = [i['title'] for i in trans['query']['embeddedin']]
    total = len(page_list)
    current = 0
    for page_title in page_list:
        current += 1
        util.log('Loading page: ', page_title)
        page = user.get_page(page_title)
        t_regex = '{{(%s)([|}])' % template_name
        replacement = "{{subst:%s" % template_name
        if template_ns.lower() == 'template':
            name = template_name.split(':', 1)[1]
            t_regex = '{{([Tt][Ee][Mm][Pp][Ll][Aa][Tt][Ee]:)?%s([|}])' % name
            replacement = "{{subst:%s" % name
        t_regex = re.compile(t_regex)
        page.text = re.sub(t_regex, replacement + r'\2', page.text)
        page.save(
            bot=1,
            summary='Substituting template %s (%i/%i)' % (template_name, current, total)
        )

