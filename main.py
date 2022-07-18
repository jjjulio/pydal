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

    artists = pydal.getLiked('artists')
    for arId in artists:

        artist = pydal.getArtist(arId)

        albums = artist.getAlbums()
        for album in albums:
            album.download()

        singles = artist.getSingles()
        for single in singles:
            single.download()

        break
    pydal.close()
except KeyboardInterrupt:
    pydal = Pydal()
    pydal.close()
    raise