from __future__ import unicode_literals
import yt_dlp
from pyfiglet import Figlet
from metadata import Metadata
import os
import sys

queue = []

if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        queue.append(sys.argv[i])

print(Figlet(font='slant').renderText('yeeet'))

def print_queue(q):
    for i in range(len(q)):
        print(str(i) + '. url: ' + q[i])

print('[c: cancel | f: finish | r <index>: remove url]')
print_queue(queue)
while True:
    url = input(str(len(queue)) + '. url: ')
    if url == 'c':
        exit(1)
    elif url == 'f':
        break
    elif url[0] == 'r':
        queue.pop(int(url[1:]))
        print('\ncurrent list:')
        print_queue(queue)
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
        print(d['filename'].split('.', 2)[0] + ' done. \nconverting . . .')


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

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(queue)

files = []
for filename in os.listdir('.'):
    if "mp3" in filename or "m4a" in filename:
        files.append(filename)

for file in files:
    print(file)
    meta = Metadata(file)
    meta.fetch()
    meta.apply()
import sys
