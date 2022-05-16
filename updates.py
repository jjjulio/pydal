from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()
    albums = pydal.getFeed()
    print("Downloading new releases!")
    count = 0
    for album in albums:
        print("Downloading New Releases: [" + str(count + 1) + "/" + str(len(albums)) + "]")
        album.download()
    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise