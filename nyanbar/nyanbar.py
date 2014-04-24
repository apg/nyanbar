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

VERSION = '0.3'

__author__ = 'Andrew Gwozdziewycz <web@apgwoz.com>'
__copyright__ = '(C) 2011, 2014 Andrew Gwozdziewycz, GNU LGPL'
__version__ = VERSION


from itertools import cycle
import threading
import time
import subprocess
import os
import signal

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

AUDIO_PLAYERS = [('afplay', []),
                 ('mpg123', ['-q',]),
                 ('mplayer', ['-really-quiet',]),
                 ]



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
next(colors); next(bgcolors); next(tail);
next(stream); next(legs); next(toast)


def find_audio_player():
    """Searches for one of the AUDIO_PLAYERS executables on the path
    """
    path = os.environ.get('PATH', '').split(':')
    for p in path:
        for a, args in AUDIO_PLAYERS:
            tp = os.path.join(p, a)
            if os.path.exists(tp) and \
                    not os.path.isdir(tp) and \
                    os.access(tp, os.X_OK):
                return [tp] + list(args)
    return None


class NyanBar(threading.Thread):

    def __init__(self, interval=100, tasks=0, visible=True, audiofile=None):
        threading.Thread.__init__(self)
        self._amount = 0
        self._interval = interval
        self._tasks = tasks
        self._tasks_done = 0
        self._finished = False
        self._audiofile = audiofile
        self._audiopid = None
        self.setDaemon(True)
        self._started = threading.Event()
        self._showing = visible
        if visible:
            self.start()

    def __enter__(self):
        self.show()
        return self

    def __exit__(self, *args):
        self.finish()

    def show(self, visible=True):
        if not self._started.is_set():
            self.start()
        self._showing = visible

    def play(self):
        if self._audiofile:
            ap = find_audio_player()
            if ap:
                args = ap + [self._audiofile]
                self._audiopid = subprocess.Popen(args).pid

    def run(self):
        self._started.set()
        self.play()
        while not self._finished:
            self._draw(self._amount)
            if self._amount >= 100:
                break
            time.sleep(self._interval / 1000.0)

    def _draw(self, amt):
        if self._showing:
            width = 35 * (amt / 100.0) # 70 characters, but stream pieces are len 2
            st = next(stream) * int(width)
            t = next(toast)
            params = (colored(st, next(colors), next(bgcolors)),
                      colored(st[:-1], next(colors), next(bgcolors)),
                      next(tail),
                      ' ' * t,
                      colored(st, next(colors), next(bgcolors)),
                      '_' * t,
                      ' ' * (len(st) + next(legs)))
            print(TEMPLATE % params)
            print("\x1b[6A") # move cursor 6 lines up

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

    def finish(self):
        self._finished = True
        print("\x1b[4B") # move cursor 4 lines down
        print("\x1b[J")

        if self._audiopid:
            # kill it.
            os.kill(self._audiopid, signal.SIGKILL)
