import wget
import os

url = 'https://hitchmap.com/dump.sqlite'
filename = 'points.sqlite'
if os.path.exists(filename):
        os.remove(filename)
wget.download(url, filename)