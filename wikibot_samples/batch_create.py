"""
batch_create

Creates a list of pages, each with the specified text.
"""

from wikibot import util

def run(user, page_list, text, edit_summary="Creating page"):
    current = 0
    total = len(page_list)
    for page_name in page_list:
        current += 1
        util.log('Loading ' + page_name)
        page = user.get_page(page_name)
        if page.text != '':
            util.log('Page has content! Skipping...')
            continue
        page.text = text
        page.save(
            bot=1,
            summary=edit_summary + (" (%i/%i)" % (current, total))
        )
    util.log("Task completed.")

