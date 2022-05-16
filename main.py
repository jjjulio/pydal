from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()
    artist = pydal.getArtist(15073663)
    #artist = pydal.getArtist(5271845)
    artist.download()
    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise