from nyanbar import NyanBar
import time

progress = NyanBar()

for n in range(100):
    time.sleep(.01)
    progress.update(n)

progress.finish()
