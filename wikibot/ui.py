"""
User interface
"""

from __future__ import division
__metaclass__ = type

import os

import wikibot
import wikibot.util as util

def getTerminalSize():
    # Found at http://stackoverflow.com/questions/566746
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

class ProgressBar():
    def __init__(self, width=80, steps=100, bar_color='blue', color='grey', char='='):
        self.width, self.steps, self.color, self.bar_color, self.char = \
            width, steps, color, bar_color, char[:1]
        self.width = min(self.width, getTerminalSize()[0])
        self.step = 0
    
    def inc(self, inc=1):
        self.step += inc
        self.update(self.step)
    
    def update(self, step=None):
        if step is None:
            step = self.step
        util.logf('\r<bold,{color}>[<bold,{bar_color}>{string:<{width}}<bold,{color}>]'.format(
            bar_color = self.bar_color,
            color = self.color,
            string = (self.char * int((self.step / self.steps) * (self.width - 2)))[:self.width-2],
            width = self.width - 2,
        ))
        
if __name__ == '__main__':
    import time, random, termcolor
    pb = ProgressBar(steps=30, bar_color='blue', width=100)
    while pb.step < pb.steps:
        pb.inc(7)
        time.sleep(.1)
    util.log()
