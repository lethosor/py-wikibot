import wikibot, time, random, termcolor
import wikibot.util as util
pb = wikibot.ui.ProgressBar(steps=100, bar_color='red', width=100)
while pb.step < pb.steps:
    pb.inc()
    time.sleep(.02)
util.log()
