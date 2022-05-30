import os
import sys
import urllib

from Pydal import *
import requests
import urllib3
import urllib
from time import sleep
import json
import base64
urllib3.disable_warnings()
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import Picture, FLAC

class Pydal(object):
    apiKey = {'clientId': 'zU4XHVVkc2tDPo4t', 'clientSecret': 'VJKhDFqJPqvsPVNBV6ukXTJmwlvbttP7wlMlrc72se4='}
    user = ""
    settings = ""
    def __init__(self):
        self.settings = self.getSettings()
        #read token from file
        try:
            with open('user.json') as json_file:
                self.user = json.load(json_file)
                #print(self.user)
            if self.settings['isrunning'] == "false":
                if self.verifyToken():
                    print("User loaded and access_token verified.")
                else:
                    print("User loaded but access_token expired or not valid, trying to get a new token")
                    self.refreshToken()
                self.settings['isrunning'] = "true"
                self.saveSettings()

        except:
            print("No User Loaded, you need to login")
            self.login()

    def close(self):
        self.settings['isrunning'] = "false"
        self.saveSettings()

    def getUser():
        with open('user.json') as json_file:
            user = json.load(json_file)
        return user

    def getSettings(self):
        with open('settings.json') as json_file:
            settings = json.load(json_file)
        return settings

    def saveSettings(self):
        with open('settings.json', 'w') as outfile:
            json.dump(self.settings, outfile)

    def getDeviceCode(self):
        url = "https://auth.tidal.com/v1/oauth2/device_authorization"
        data = {'client_id': self.apiKey['clientId'], 'scope': 'r_usr+w_usr+w_sub'}
        response = requests.post(url, data=data, auth=None, verify=False).json()
        if 'status' in response and response['status'] != 200:
            print("Device authorization failed. Please try again.")
            check = False
        else:
            check = True
        return response, check


    def checkAuth(self, deviceCode):
        url = 'https://auth.tidal.com/v1/oauth2/token'
        data = {'client_id': self.apiKey['clientId'], 'device_code': deviceCode,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code', 'scope': 'r_usr+w_usr+w_sub'}
        response = requests.post(url, data=data, auth=(self.apiKey['clientId'], self.apiKey['clientSecret']), verify=False).json()
        if 'access_token' in response:
            check = True
        else:
            check = False
        return response, check


    def verifyToken(self):
        #print("--->" + self.user['access_token'])
        header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
        response = requests.get('https://api.tidal.com/v1/sessions', headers=header).json()
        #print(response)
        if 'sessionId' in response:
            return True
        return False

    def refreshToken(self):
        url = 'https://auth.tidal.com/v1/oauth2/token'

        data = {'client_id': self.apiKey['clientId'], 'refresh_token': self.user['refresh_token'], 'grant_type': 'refresh_token',
                'scope': 'r_usr+w_usr+w_sub'}
        result = requests.post(url, data=data, auth=(self.apiKey['clientId'], self.apiKey['clientSecret']), verify=False).json()
        # print(result)
        if 'access_token' in result:
            self.user['access_token'] = result['access_token']
            with open('user.json', 'w') as outfile:
                json.dump(self.user, outfile)
            return result
        else:
            print('error getting new token :(, please investigate')
            return False

    def login(self):
        deviceCodeResponse, check = self.getDeviceCode()
        print(deviceCodeResponse)
        if check:
            deviceCode = deviceCodeResponse['deviceCode']
        else:
            #print(deviceCodeResponse)
            return

        print("Please authorize this device on your tidal account: ")
        print("Code: " + deviceCodeResponse['userCode'])
        print("Link: " + deviceCodeResponse['verificationUri'])
        print("Full URL: https://" + deviceCodeResponse['verificationUriComplete'])

        print("Waiting For authorization...")
        leftTime = deviceCodeResponse['expiresIn']
        while leftTime > 0:
            sleep(deviceCodeResponse['interval'])
            leftTime -= deviceCodeResponse['interval']
            checkAuthResponse, check = self.checkAuth(deviceCodeResponse['deviceCode'])
            if check:
                print(checkAuthResponse)
                with open('user.json', 'w') as outfile:
                    json.dump(checkAuthResponse, outfile)
                return checkAuthResponse
                print("Logged in!")
                break
        if leftTime == 0:
            print("Device no authorized on time, sorry :C")
            return False

    def getArtist(self, artistId):
        try:
            with open('./DB/artists/' + str(artistId) + '.json') as json_file:
                response = json.load(json_file)
        except:
            url = 'https://api.tidal.com/v1/artists/' + str(artistId)
            paras = {'countryCode': self.user['user']['countryCode'], 'limit': 1}
            header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
            response = requests.get(url, headers=header, params=paras).json()
            with open('./DB/artists/' + str(artistId) + '.json', 'w') as outfile:
                json.dump(response, outfile)
        #print(response)
        return Artist(response)

    def getAlbum(self, albumId):
        try:
            with open('./DB/albums/' + str(albumId) + '.json') as json_file:
                response = json.load(json_file)
        except:
            url = 'https://api.tidal.com/v1/albums/' + str(albumId)
            paras = {'countryCode': self.user['user']['countryCode'], 'limit': 1}
            header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
            response = requests.get(url, headers=header, params=paras).json()
            with open('./DB/albums/' + str(albumId) + '.json', 'w') as outfile:
                json.dump(response, outfile)
        return Album(response)

    def getLiked(self, type):
        url = 'https://api.tidal.com/v1/users/{}/favorites/ids'.format(str(self.user['user']['userId']))
        paras = {'countryCode': self.user['user']['countryCode']}
        header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
        response = requests.get(url, headers=header, params=paras).json()
        # print(response)
        if type == 'all':
            return response
        if type == 'videos':
            return response['VIDEO']
        if type == 'artists':
            return response['ARTIST']
        if type == 'albums':
            return response['ALBUM']
        if type == 'tracks':
            return response['TRACK']
        if type == 'playlists':
            return response['PLAYLIST']

    def getFeed(self):
        url = 'https://api.tidal.com/v2/feed/activities/'
        paras = {'countryCode': self.user['user']['countryCode'], 'locale': 'en-us', 'userId': self.user['user']['userId']}
        header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
        response = requests.get(url, headers=header, params=paras).json()
        albums = []
        for activity in response['activities']:
            if 'album' in activity['followableActivity']:
                albums.append(self.getAlbum(activity['followableActivity']['album']['id']))
        return albums

    def deleteFavorite(self, type, id):
        url = 'https://api.tidal.com/v1/users/' + str(self.user['user']['userId']) + '/favorites/' + type + '/' + str(id)
        print(url)
        paras = {'countryCode': self.user['user']['countryCode']}
        header = {'authorization': 'Bearer {}'.format(self.user['access_token'])}
        response = requests.delete(url, headers=header, params=paras)
        print(response)
        return response

class Artist(object):

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.picture = data['picture']
        try:
            self.artistTypes = data['artistTypes']
            self.url = data['url']
            self.mixes = data['mixes']
        except:
            pass

    def getPath(self):
        return Pydal().getSettings()['downloadpath'] + "" + self.name[0].upper() + '/' + self.name.replace("/", "-").replace(":"," -") + '/'

    def getVideosPath(self):
        return Pydal().getSettings()['downloadpath'] + "Videos/" + self.name[0].upper() + '/' + self.name.replace("/", "-").replace(":"," -") + '/'

    def getPictureUrl(self):
        url = "https://resources.tidal.com/images/"
        if self.picture != None:
            return url + self.picture.replace("-", "/") + "/750x750.jpg"
        else:
            return None

    def downloadPicture(self):
        fileName = self.getPath() + 'Picture.jpg'
        if self.picture == None or os.path.isfile(fileName):
            # print("Artist does not have cover or cover already downloaded")
            return
        try:
            os.makedirs(self.getPath())
        except OSError as error:
            pass
        # try:
        urllib.request.urlretrieve(self.getPictureUrl(), fileName)


    def getAlbums(self):
        url = 'https://api.tidal.com/v1/artists/' + str(self.id) + '/albums'
        paras = {'countryCode': Pydal.getUser()['user']['countryCode'], 'limit': 9999, 'filter': 'EPSANDSINGLES'}
        header = {'authorization': 'Bearer {}'.format(Pydal.getUser()['access_token'])}
        response = requests.get(url, headers=header, params=paras).json()
        singles = []
        for album in response['items']:
            singles.append(Album(album))
        return singles


    def getSingles(self ):
        url = 'https://api.tidal.com/v1/artists/' + str(self.id) + '/albums'
        paras = {'countryCode': Pydal.getUser()['user']['countryCode'], 'limit': 9999}
        header = {'authorization': 'Bearer {}'.format(Pydal.getUser()['access_token'])}
        response = requests.get(url, headers=header, params=paras).json()
        albums = []
        for album in response['items']:
            albums.append(Album(album))
        return albums

    def download(self):
        try:
            with open('./DB/downloaded/artists.txt') as myfile:
                if str(self.id) in myfile.read():
                    print("Artist: " + self.name + " already downloaded, skipping...")
                    return
        except:
            pass
        print("==========================================================")
        print("Downloading Artist ===> " + self.name + "\n\n")
        self.downloadPicture()
        albums = self.getAlbums()
        singles = self.getSingles()
        count = 0
        for album in albums:
            print("Downloading Albums: [" + str(count + 1) + "/" + str(len(albums)) + "]")
            album.download()
            count += 1

        count = 0
        for single in singles:
            print("Downloading Singles: [" + str(count + 1) + "/" + str(len(singles)) + "]")
            single.download()
            count += 1
        print("==========================================================")
        os.system("echo " + str(self.id) + " >> ./DB/downloaded/artists.txt")
        return True

class Album(object):

    def __init__(self, data):
        self.id = str(data['id'])
        self.title = data['title']
        self.cover = data['cover']
        try:
            self.duration = data['duration']
            self.streamReady = data['streamReady']
            self.streamStartDate = data['streamStartDate']
            self.allowStreaming = data['allowStreaming']
            self.premiumStreamingOnly = data['premiumStreamingOnly']
            self.numberOfTracks = data['numberOfTracks']
            self.numberOfVideos = data['numberOfVideos']
            self.numberOfVolumes = data['numberOfVolumes']
            self.releaseDate = data['releaseDate']
            self.copyright = data['copyright']
            self.type = data['type']
            self.version = data['version']
            self.url = data['url']
            self.videoCover = ['videoCover']
            self.explicit = data['explicit']
            self.upc = data['upc']
            self.audioQuality = data['audioQuality']
            self.artist = Artist(data['artist'])
            self.artists = []
            for albumArtist in data['artists']:
                self.artists.append(Artist(albumArtist))
        except:
            pass

    def getYear(self):
        return self.releaseDate.split("-")[0]

    def getPath(self):
        tag = ''
        single = ''
        if self.audioQuality == 'HI_RES':
            tag += '[M]'
        if self.explicit == 'true':
            tag += '[E]'

        tag += ' '
        if self.type == 'SINGLE' or self.type == 'EP':
            albumPath = self.artist.getPath() + 'Singles/[' + str(self.getYear()) + '] ' + tag + self.title.replace("/","-").replace(":", " -").replace("\\", "-").replace(":", "-").replace("*", "x").replace("?", "").replace("\"","").replace("<", "").replace(">", "").replace("|", "").replace("¿", "")
        else:
            albumPath = self.artist.getPath() + '[' + str(self.getYear()) + '] ' + tag + self.title.replace("/","-").replace(":"," -").replace("\\", "-").replace(":", "-").replace("*", "x").replace("?", "").replace("\"", "").replace("<","").replace(">", "").replace("|", "").replace("¿", "")

        if os.path.exists(albumPath):
            albumPath = albumPath + ' [' + str(self.id) + ']/'

        return albumPath

    def getCoverUrl(self):
        url = "https://resources.tidal.com/images/"
        if self.cover != None:
            return url + self.cover.replace("-", "/") + "/1280x1280.jpg"
        else:
            return None

    def downloadCover(self):
        fileName = self.getPath() + 'Cover.jpg'
        if self.cover == None or os.path.isfile(fileName):
            # print("Album does not have cover or cover already downloaded")
            return
        try:
            os.makedirs(self.getPath())
        except OSError as error:
            pass
        # try:
        urllib.request.urlretrieve(self.getCoverUrl(), fileName)


    def getCoverFileName(self):
        return self.getPath() + 'Cover.jpg'

    def getTracks(self):
        url = 'https://api.tidal.com/v1/albums/' + str(self.id) + '/items'
        paras = {'countryCode': Pydal.getUser()['user']['countryCode'], 'limit': 100}
        header = {'authorization': 'Bearer {}'.format(Pydal.getUser()['access_token'])}
        response = requests.get(url, headers=header, params=paras).json()
        #print(response)
        tracks = []
        for track in response['items']:
            tracks.append(Track(track['item']))
        return tracks

    def download(self):
        try:
            with open('./DB/downloaded/albums.txt') as myfile:
                if str(self.id) in myfile.read():
                    print("Album: " + self.title + " already downloaded, skipping...")
                    return False
        except:
            pass
        print("----------------------------------------------------------")
        self.downloadCover()
        sleep(1.5)
        print("\n" + self.artist.name + " - " + self.title + "\n")
        tracks = self.getTracks()
        for track in tracks:
            track.download()
        scanUrl = "http://altair.usbx.me:12075/library/sections/5/refresh?path=" + urllib.parse.quote_plus(self.getPath()) + "&X-Plex-Token=Typea5Ncd-aJ8yp8x1VV"
        os.system("echo " + str(self.id) + " >> ./DB/downloaded/albums.txt")
        requests.get(scanUrl)
        sleep(self.numberOfTracks*1.5)
        print("----------------------------------------------------------")
        return True


class Track(object):

    def __init__(self, data):
        #print(data)
        self.id = data['id']
        self.title = data['title']
        self.duration = data['duration']
        try:
            self.type = data['type']
        except:
            self.type = "unkown"
        try: #this is if item is music video
            self.replayGain = data['replayGain']
            self.peak = data['peak']
            self.premiumStreamingOnly = data['premiumStreamingOnly']
            self.version = data['version']
            self.copyright = data['copyright']
            self.url = data['url']
            self.isrc = data['isrc']
            self.editable = data['editable']
            self.audioQuality = data['audioQuality']
            self.audioModes = data['audioModes']
            self.mixes = data['mixes']
        except:
            pass
        self.allowStreaming = data['allowStreaming']
        self.streamReady = data['streamReady']
        self.streamStartDate = data['streamStartDate']
        self.trackNumber = data['trackNumber']
        self.volumeNumber = data['volumeNumber']
        self.popularity = data['popularity']
        self.explicit = data['explicit']
        self.artist = Pydal().getArtist(data['artist']['id'])
        self.artists = []
        for trackArtist in data['artists']:
            try:
                self.artists.append(Pydal().getArtist(trackArtist['id']))
            except:
                pass
        self.album = Pydal().getAlbum(data['album']['id'])


    def getPath(self):
        if self.album.numberOfVolumes > 1:
            return self.album.getPath() + 'CD ' + str(self.volumeNumber) + '/'  # + str(self.trackNumber) + ' ' + self.title.replace("/","-").replace(":"," -")
        else:
            return self.album.getPath()  # + str(self.trackNumber) + ' ' + self.title.replace("/","-").replace(":"," -")


    def getDownloadUrl(self):
        url = 'https://api.tidal.com/v1/tracks/' + str(self.id) + '/playbackinfopostpaywall'
        paras = {"audioquality": "HI_RES", "playbackmode": "STREAM", "assetpresentation": "FULL"}
        header = {'authorization': 'Bearer {}'.format(Pydal.getUser()['access_token'])}
        response = {'none': 'none'}
        attemps = 5
        while 'manifest' not in response:
            if attemps == 0:
                return "nourltrack"
            try:
                response = requests.get(url, headers=header, params=paras).json()
            except:
                print(response)
                print("Error in request... retrying")
                sleep(3.0)
            attemps = attemps - 1

        manifest = json.loads(base64.b64decode(response['manifest']).decode('utf-8'))
        url = manifest['urls'][0]
        return url

    def getArtists(self):
        trackArtists = ""
        z = 0
        for art in self.artists:
            z += 1
            if z == len(self.artists):
                trackArtists += art.name
            else:
                trackArtists += art.name + ","
        return trackArtists

    def getAlbumYear(self):
        return self.album.releaseDate.split("-")[0]

    def getLyricsFileName(self):
        if self.album.numberOfVolumes > 1:
            return self.album.getPath() + 'CD ' + str(self.volumeNumber) + '/' + str(self.trackNumber) + ' ' + self.title.replace("/", "-").replace(":", " -").replace("\\", "-").replace(":", "-").replace("*", "x").replace("?", "").replace("\"", "").replace("<", "").replace(">","").replace("|","").replace("¿", "") + '.lrc'
        else:
            return self.album.getPath() + str(self.trackNumber) + ' ' + self.title.replace("/", "-").replace(":"," -").replace("\\", "-").replace(":", "-").replace("*", "x").replace("?", "").replace("\"", "").replace("<","").replace(">", "").replace("|", "").replace("¿", "") + '.lrc'

    def getLyrics(self):
        url = 'https://api.tidal.com/v1/tracks/' + str(self.id) + '/lyrics'
        paras = {'countryCode': Pydal.getUser()['user']['countryCode'], 'limit': 1}
        header = {'authorization': 'Bearer {}'.format(Pydal.getUser()['access_token'])}
        pased = 0
        while pased == 0:
            try:
                response = requests.get(url, headers=header, params=paras).json()
                pased = 1
            except:
                print("Error getting lyrics, trying again")
                sleep(2)

        if 'subtitles' in response:
            return response
        else:
            return None

    def getLyricsType(self, type):
        response = self.getLyrics()
        if response != None:
            lyrics = "Artist:\t\t" + self.artist.name + "\n"
            if self.artist.name != self.getArtists():
                lyrics += "Artists:\t" + self.getArtists() + "\n"
            lyrics += "Album:\t\t" + self.album.title + "\n"
            lyrics += "Title:\t\t" + self.title + "\n\n\n"
            if type == 's':
                if response['subtitles'] != None:
                    lyrics += response['subtitles']
                else:
                    return None
            else:
                if response['lyrics'] != None:
                    lyrics += response['lyrics']
                else:
                    return None
            return lyrics
        else:
            return None

    def downloadLyrics(self):
        lyric = self.getLyricsType('s')
        if lyric != None:
            with open(self.getLyricsFileName(), "w", encoding="utf-8") as f:
                f.write(lyric)

    def download(self):
        if self.type.lower() == "music video":
            print("Not downloading videos yet")
            return

        trackName = self.getPath() + str(self.trackNumber) + ' ' + self.title.replace("/", "-").replace(":"," -").replace("\\", "-").replace(":", "-").replace("*", "x").replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "").replace("¿", "")
        #if os.path.isfile(trackName + ".flac") or os.path.isfile(trackName + ".m4a"):
        #    print("Track file exists for: " + self.title + ", skipping")
        #    return

        if not self.allowStreaming:
            return

        if not self.streamReady:
            print("[ " + str(self.trackNumber) + " " + self.title + " ] Not ready for download")
            return

        url = self.getDownloadUrl()
        if "nourltrack" in url:
            print("unable to download track: " + self.title + " retrying")
            sleep(2.0)
            url = self.getDownloadUrl()
            if "nourltrack" in url:
                print("unable to download track: " + self.title + " skipping")
                return
        ext = None
        #self.artist.downloadPicture()
        #self.album.downloadCover()
        sleep(0.5)
        if ".flac" in url:
            ext = ".flac"
        else:
            ext = ".m4a"

        trackFile = trackName + ext

        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')
        path = self.getPath()

        try:
            os.makedirs(path)
        except OSError as error:
            pass

        trackPrint = str(self.trackNumber) + " " + self.title
        # print(trackPrint)
        with open(trackFile, 'wb') as f:

            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(100 * downloaded / total)
                    progress = ''
                    cp = done * len(trackPrint) / 100
                    count = 0
                    while count < cp:
                        progress += trackPrint[count]
                        count += 1
                    # sys.stdout.write('\t\r[{}{}]'.format('-' * done, '_' * (100-done)))
                    sys.stdout.write('\r[{}]'.format(progress))
                    sys.stdout.flush()
        sys.stdout.write('\n')
        # print(trackPrint, flush=True)
        sys.stdout.flush()
        self.setTags(trackFile)
        self.downloadLyrics()

    def setTags(self, trackFile):
        trackFile = trackFile
        lyric = self.getLyricsType('l')
        if trackFile.endswith('.flac'):
            audio = FLAC(trackFile)
            audio["title"] = self.title
            audio["artist"] = self.getArtists()
            audio["album"] = self.album.title
            audio["artists"] = self.artist.name
            audio["copyright"] = str(self.copyright)
            audio["isrc"] = self.isrc
            audio["trackNumber"] = str(self.trackNumber)
            audio["tracktotal"] = str(self.album.numberOfTracks)
            audio["discnumber"] = str(self.volumeNumber)
            audio["disctotal"] = str(self.album.numberOfVolumes)
            audio["albumartist"] = self.album.artist.name
            audio["year"] = self.album.getYear()
            audio["date"] = self.album.releaseDate
            if lyric != None:
                audio["lyrics"] = lyric
            if self.album.cover != None:
                cover = Picture()
                with open(self.album.getCoverFileName(), "rb") as f:
                    cover.data = f.read()
                    cover.type = 3
                    cover.desc = "Front Cover"
                    cover.mime = u"image/jpeg"
                    cover.width = 1280
                    cover.height = 1280
                    cover.depth = 16
                    audio.add_picture(picture=cover)
            audio.pprint()
            audio.save()

        if trackFile.endswith('.m4a'):
            audio = MP4(trackFile)
            audio["\xa9nam"] = self.title
            audio["\xa9ART"] = self.getArtists()
            audio["\xa9alb"] = self.album.title
            audio["aART"] = self.artist.name
            audio["cprt"] = str(self.copyright)
            audio["\xa9day"] = str(self.album.releaseDate.split("-")[0]), self.album.releaseDate
            audio["trkn"] = [(self.trackNumber, self.album.numberOfTracks)]
            audio["disk"] = [(self.volumeNumber, self.album.numberOfVolumes)]
            audio["soaa"] = self.album.artist.name
            audio["ISRC"] = self.isrc
            if lyric != None:
                audio['\xa9lyr'] = lyric
            if self.album.cover != None:
                with open(self.album.getCoverFileName(), "rb") as f:
                    audio["covr"] = [MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)]
            audio.pprint()
            audio.save()