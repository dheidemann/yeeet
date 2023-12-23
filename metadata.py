import os
import spotipy
import urllib.request
import sys
import eyed3
from spotipy.oauth2 import SpotifyClientCredentials
import discogs_client
import lyricsgenius

from credentials import *

class Metadata:
    def __init__(self, filename):
        self.filename = filename
        self.filename_old = filename

    def manual_input(self):
        self.title = input('title: ')
        self.artist = input('artist: ')
        self.album = input('album: ')
        self.filename = self.title + ' - ' + self.artist


    def fetch(self):
        spotify_credentials = SpotifyClientCredentials(
            client_id=SPOTIFY_CID, 
            client_secret=SPOTIFY_CS
        )
        d = discogs_client.Client(
            'yeeet/1.0',
            user_token = DISCOGS_PAT
        )
        genius = lyricsgenius.Genius(GENIUS_AT)

        sp = spotipy.Spotify(client_credentials_manager = spotify_credentials)
        text_file = open('Blacklist.txt', 'r')
        blacklist_words = text_file.read().splitlines();
        blacklist_words = [word.lower() for word in blacklist_words]

        search_text = self.filename[0:-4].lower();
        extension = self.filename[-4:];
        if '(official music video)' in search_text:
            search_text = search_text.replace('(official music video)', '')
        for word in search_text.split('.')[0].split(' '):
            if word in blacklist_words:
                search_text = search_text.replace(word, '')

        spotify_res = sp.search(search_text, limit=5)
        discogs_res = d.search(search_text, type='release')

        if (len(spotify_res['tracks']['items']) == 0 and discogs_res.pages == 0):
            sys.stderr.write('No data found\nPlease enter information manually:')
            manual_input()
        else:
            num = 0
            for track in spotify_res['tracks']['items']:
                print(str(num) + ' [spotify]: ' + str(track['artists'][0]['name']) + ' - ' + str(track['name']))
                num += 1
            for i in range(min(discogs_res.pages, 5)):
                print(str(num) + ' [discogs]: ' + discogs_res[i].artists[0].name + ' - ' + discogs_res[i].title)
                num += 1

            selected = input('choose result [m: manual input, default: 0]: ')
            if selected == '': selected = 0
            elif selected == 'm': manual_input()
            selected = int(selected)
            if selected < len(spotify_res['tracks']['items']):
                self.title = spotify_res['tracks']['items'][selected]['name']
                self.artist = spotify_res['tracks']['items'][selected]['artists'][0]['name']
                self.album = spotify_res['tracks']['items'][selected]['album']['name']
                albumart_url = spotify_res['tracks']['items'][selected]['album']['images'][0]['url']
            else:
                d_index = selected - len(spotify_res['tracks']['items'])
                self.title = discogs_res[d_index].title
                self.artist = discogs_res[d_index].artists[0].name
                albumart_url = discogs_res[d_index].images[0]['uri']

            self.filename = self.title + ' - ' + self.artist
            try:
                self.album_art_filename = self.filename + ".jpg"
                urllib.request.urlretrieve(albumart_url, self.album_art_filename);
            except:
                sys.stderr.write('Cant download artwork @' + albumart_url+'\n')
                self.album_art_filename = '';
                pass

        print('\nfetch lyrics ...')
        try:
            song = genius.search_song(self.title, self.artist)
            self.lyrics = song.lyrics
        except:
            sys.stderr.write('Cant find ' + self.filename + ' on genius\n')
            self.lyrics = '';
            pass
        
        self.filename += extension

    def apply(self):
        try:
            os.rename(self.filename_old, self.filename)
        except:
            print("can't rename file " + self.filename_old)

        songfd = eyed3.load(self.filename);
        tag = songfd.tag;
        if tag is not None:
            try: 
                if self.title != '':
                    tag.title = self.title
                if self.artist != '':
                    tag.artist = self.artist
                if self.album != '':
                    tag.album = self.album
                if self.album_art_filename != '':
                    imagedata = open(self.cover_art_filename,"rb").read()
                    tag.images.set(3,imagedata,"image/jpeg")
                if self.lyrics is not None:
                    tag.lyrics.set(self.lyrics);
            except:
                pass;
            tag.save();
