from Pydal import *
import os
from time import sleep


try:
    pydal = Pydal()
    albums = pydal.getLiked('albums')
    #print(artists)
    limit = 300
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