from nyanbar import NyanBar
import time

progress = NyanBar(audiofile="NyanCat-original.mp3")

for n in range(100):
    time.sleep(.3)
    progress.update(n)

progress.finish()
