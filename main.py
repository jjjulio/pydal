from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()
    artists = pydal.getLiked('artists')
    print(artists)
    limit = 2
    count = 0
    for artistId in artists:
        artist = pydal.getArtist(artistId)
        if artist.download():
            count += 1
        if count == limit:
            break
    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise