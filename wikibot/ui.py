"""
User interface
"""

from __future__ import division
__metaclass__ = type

import os
import sys

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

class ProgressBar:
    def __init__(self, width=80, steps=100, bar_color='blue', color='grey', char='='):
        self.width, self.steps, self.color, self.bar_color, self.char = \
            width, steps, color, bar_color, char[:1]
        self.width = min(self.width, getTerminalSize()[0])
        # List of 10 integers which occur near multiples of 10%
        self.marks = [int(x / 10 * self.steps) for x in range(1, 11)]
        self.step = 0
    
    def inc(self, inc=1):
        self.step += inc
        self.update(self.step)
    
    def update(self, step=None):
        if step is None:
            step = self.step
        if sys.stdout.isatty():
            width = self.width - 2  # Compensate for beginning/end markers
            string = (self.char * int((self.step / self.steps) * width) + '<>')[:width+2]  # Compensate for <>
            util.logf('\r<bold,{color}>[<bold,{bar_color}>{string:<{width}}<bold,{color}>]'.format(
                bar_color = self.bar_color,
                color = self.color,
                string = string,
                width = width + 2,  # Compensate for <>
            ))
        else:
            if step in self.marks:
                i = self.marks.index(step) + 1
                util.logf('%d%%\n' % (i * 10))

class IndefProgressBar:
    # <cyan,bold>=<blue,bold>=<cyan,bold>=
    def __init__(self, width=80, bar=' <cyan,bold>=<blue,bold>=<cyan,bold>=', color='grey'):
        self.index = 0
        self.width, self.color = min(width, getTerminalSize()[0]), color
        self.bar, self.bar_len = bar, len(util._log_parse(bar, color=False))
        self.full_bar = self.bar * int(self.width / self.bar_len + 1)  # Round up
        self.full_bar = self.full_bar.replace('<', '\x01<').replace('>', '>\x01')  # Markers
    
    def update(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.bar_len - 1
        if sys.stdout.isatty():
            util.logf('\r<bold,{color}>[<>{bar}<bold,{color}>]'.format(
                bar = self.get_bar(),
                color = self.color,
            ))
        else:
            util.logf('.')
    
    def get_bar(self, index=None, width=None):
        if index is None:
            index = self.index
        if width is None:
            width = self.width - 2
        parts = self.full_bar.split('\x01')
        chars = []
        for p in parts:
            if p.startswith('<'):
                chars.append((p, 0))
            else:
                for c in p:
                    chars.append((c, 1))
        length = 0 - index
        bar = ''
        for c in chars:
            length += c[1]
            if length > width:
                break
            if length > 0 or not c[1]:
                bar += c[0]
        return bar
