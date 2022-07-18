from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()

    limit = 2
    count = 0
    artists = pydal.getLiked('artists')
    for arId in artists:
        artist = pydal.getArtist(arId)

        if artist.download():
            count += 1
        if count == limit:
            break


    albums = pydal.getLiked('albums')
    limit = 10
    count = 0
    for albumId in albums:
        album = pydal.getAlbum(albumId)
        if album.download():
            count += 1
        if count == limit:
            break



    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise