import wikibot, time, random, termcolor
import wikibot.util as util
pb = wikibot.ui.IndefProgressBar(width=96)
try:
    while 1:
        pb.update()
        time.sleep(0.1)
except:
    pass
util.log()