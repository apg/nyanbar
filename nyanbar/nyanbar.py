"""NyanBar - a Nyan Cat progress bar for python

Example:

progress = NyanBar()
# do some work
progress.update(20) # update always takes where you are now

Or...

progress = NyanBar(tasks=100)
# do some work.
progress.task_done()

"""

VERSION = '0.1'

__author__ = 'Andrew Gwozdziewycz <web@apgwoz.com>'
__copyright__ = '(C) 2011 Andrew Gwozdziewycz, GNU LGPL'
__version__ = VERSION



from itertools import cycle
import threading, time

ON = "~_"
OFF = "_-"
TAILDIFF = -2
TEMPLATE = '''\x1b[2K%s,------,
\x1b[2K%s%s| %s /\\_/\\
\x1b[2K%s|_%s( ^ w^)
\x1b[2K%s    "  "
'''
FOREGROUND = "\x1b[1;%dm"
BACKGROUNDED = "\x1b[1;%d;%dm"
RESET = "\x1b[0;m"

BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37

SAVE_CURSOR = "\x1b[s"
RESTORE_CURSOR = "\x1b[u"
ERASE_REST = "\x1b[J"


def background(color):
    return color + 10


def colored(text, fg, bg=None):
    c = FOREGROUND % fg
    if bg:
        c = BACKGROUNDED % (fg, bg)

    return "%s%s%s" % (c, text, RESET)


colors = cycle([RED, YELLOW, GREEN, BLUE, MAGENTA, CYAN, GREEN])
bgcolors = cycle(map(background, [RED, YELLOW, GREEN, BLUE, MAGENTA, CYAN, GREEN]))
tail = cycle(['v', '~', '^', '~'])
legs = cycle([-1, 0, 1])
stream = cycle([ON, OFF])
toast = cycle([1, 2])
colors.next(); bgcolors.next(); tail.next(); 
stream.next(); legs.next(); toast.next()


class NyanBar(threading.Thread):

    def __init__(self, interval=100, tasks=0):
        threading.Thread.__init__(self)
        self._amount = 0
        self._interval = interval
        self._tasks = tasks
        self._tasks_done = 0
        self._finished = False
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self._finished:
            self._draw(self._amount)
            if self._amount >= 100:
                self._finish()
            time.sleep(self._interval / 1000.0)

    def _draw(self, amt):
        width = 35 * (amt / 100.0) # 70 characters, but stream pieces are len 2
        st = stream.next() * int(width)
        t = toast.next()
        params = (colored(st, colors.next(), bgcolors.next()),
                  colored(st[:-1], colors.next(), bgcolors.next()),
                  tail.next(),
                  ' ' * t,
                  colored(st, colors.next(), bgcolors.next()),
                  '_' * t,
                  ' ' * (len(st) + legs.next()))
        print TEMPLATE % params
        print "\x1b[6A" # move cursor 6 lines up

    def _finish(self):
        print "\x1b[4B" # move cursor 4 lines down
        print "\x1b[J"
        self._finished = True

    def update(self, progress):
        if progress < 0:
            progress = 0
        elif progress > 100:
            progress = 100
        self._amount = progress

    def task_done(self):
        if self._tasks > 0:
            self._tasks_done += 1
            self.update(int(100 * self._tasks_done / self._tasks))


