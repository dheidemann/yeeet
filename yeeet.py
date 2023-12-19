from __future__ import unicode_literals
import youtube_dl
from pyfiglet import Figlet
from metadata import Metadata
import os

print(Figlet(font='slant').renderText('yeeet'))

queue = []
print('[c: cancel | f: finish | r <index>: remove url]')
while True:
    url = input(str(len(queue)) + '. url: ')
    if url == 'c':
        exit(1)
    elif url == 'f':
        break
    elif url[0] == 'r':
        queue.pop(int(url[1:]))
        print('\ncurrent list:')
        for i in range(len(queue)): print(str(i) + '. url: ' + queue[i])
    else: queue.append(url)

class Logger(object):
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print(d['filename'][:-5] + ' done. \nconverting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': Logger(),
    'progress_hooks': [my_hook],
    'outtmpl': '%(title)s.%(ext)s',
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(queue)

for filename in os.listdir('.'):
    if "mp3" in filename or "m4a" in filename:
        print(filename)
        meta = Metadata(filename)
        meta.fetch()
        meta.apply()
