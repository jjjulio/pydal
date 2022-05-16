from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()
    albums = pydal.getFeed()
    print("Downloading new releases!")
    for album in albums:
        album.download()
    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise