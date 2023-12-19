import os
import spotipy
from PyLyrics import *
import urllib.request
import sys
import eyed3
from spotipy.oauth2 import SpotifyClientCredentials

from credentials import SPOTIFY_CID, SPOTIFY_CS

class Metadata:
    def __init__(self, filename):
        self.filename = filename
        self.filename_old = filename

    def fetch(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CID, client_secret=SPOTIFY_CS)
        sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
        text_file = open('Blacklist.txt', 'r')
        blacklistWords = text_file.read().splitlines();
        blacklistWords = [word.lower() for word in blacklistWords]

        searchText = self.filename[0:-4].lower();
        extension = self.filename[-4:];
        if '(official music video)' in searchText:
            searchText = searchText.replace('(official music video)', '')
        for word in searchText.split('.')[0].split(' '):
            if word in blacklistWords:
                searchText = searchText.replace(word, '')

        results = sp.search(searchText , limit=5)
        #if no results found for that file
        if (len(results['tracks']['items'])==0):
            sys.stderr.write('No data found\nPlease enter information manually:')
            self.title = input('title: ')
            self.artist = input('artist: ')
            self.album = input('album: ')
            self.filename = self.title + ' - ' + self.artist
        else:
            for i, track in enumerate(results['tracks']['items']):
                print(str(i) + ': ' + str(track['name']) + ' - ' + str(track['artists'][0]['name']))

            selected = input('choose result [default: 0]: ')
            if selected == '': selected = 0
            int(selected)
            self.title = results['tracks']['items'][selected]['name']
            self.artist = results['tracks']['items'][selected]['artists'][0]['name']
            self.album = results['tracks']['items'][selected]['album']['name']
            self.filename = self.title + ' - ' + self.artist
            albumart_url = results['tracks']['items'][selected]['album']['images'][0]['url']

            #print artist.decode('utf-8');
            try:
                self.album_art_filename = self.filename + ".jpg"
                urllib.request.urlretrieve(albumart_url, self.album_art_filename);
            except:
                sys.stderr.write('Cant download artwork @' + albumart_url+'\n')
                self.album_art_filename = '';
                pass

        try:
            self.lyrics = PyLyrics.getLyrics(self.artist, self.title, features="lxml");
        except:
            sys.stderr.write('Cant find ' + self.filename + ' on lyrics.wikia.com\n')
            self.lyrics = '';
            pass
        
        self.filename += '.mp3'

    def apply(self):
        try:
            os.rename(self.filename_old, self.filename)
        except:
            print("can't rename file " + self.filename_old)

        songfd = eyed3.load(self.filename);
        #None is returned when the file type (i.e. mime-type) is not recognized
        tag = songfd.tag;
        if tag is not None:
            try: 
                if self.title != '':
                    tag.title = self.title
                if self.artist != '':
                    tag.artist = self.artist
                if self.album != '':
                    tag.album = self.album
                if self.coverart != '':
                    imagedata = open(self.cover_art_filename,"rb").read()
                    tag.images.set(3,imagedata,"image/jpeg")

                # append image to tags
                if lyrics is not None:
                    tag.lyrics.set(lyrics);
            except:
                pass;
            tag.save();
