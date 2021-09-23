from helpers import *
import lyricsgenius
from spotipy import Spotify, SpotifyOAuth, util, CacheFileHandler
import requests
from fuzzywuzzy import fuzz
import sqlite3 as sql
import re
from dotenv import load_dotenv
import os
from sys import platform

load_dotenv()

genius = lyricsgenius.Genius(os.environ.get("GENIUS_SECRET"))

cache_handler = CacheFileHandler(cache_path="")
auth_manager = SpotifyOAuth(scope='user-read-playback-state', cache_handler=cache_handler)
spotify = Spotify(auth_manager=auth_manager)


def get_features(song):
    """Fetches audio features from Spotify Api"""
    return spotify.audio_features(song['uri'])[0]


def get_playback():
    """Returns currently playing song from Spotify api and True if connection to Spotify API worked"""
    # Query spotify API
    api_playback = spotify.current_playback()
    if api_playback:
        return api_playback['item'], True

    # Try checking name of spotify window on system
    local_playback = get_local_playback()
    if local_playback:
        return local_playback, False
    return None, False


def get_local_playback():
    """ Attempts to get the name and artist of song by checking main spotify window """
    if platform == "linux" or platform == "linux2":
        # linux
        pass
    elif platform == "darwin":
        # OS X
        pass
    elif platform == "win32":
        # windows
        pass
    return None

def get_lyrics(song):
    """Look for the lyrics either in the database or on genius.com"""

    if not song:
        print("no playback")
        return "Nothing is playing"

    verify_database()
    db_result = search_database(song['uri'])
    if db_result:
        print("Getting lyrics from database")
        return db_result

    genius_result = search_genius(song)
    if genius_result:
        print("Lyrics found on Genius - adding to database")
        addLyrics(song['uri'], song['name'], parse_artists(song['artists']), genius_result)
        return genius_result

    return "Lyrics not found"


def download_cover(song):
    """Saves the cover of song being played to cover.jpg"""
    cover = song['album']['images'][0]['url']
    img = requests.get(cover).content
    with open('cover.jpg', 'wb') as handler:
        handler.write(img)


def addLyrics(uri, name, artists, lyrics):
    """Adds new lyrics to the database along with the song uri"""
    connection = sql.connect("lyrics.db")
    crs = connection.cursor()
    comd = "INSERT INTO lyrics (id, name, artists, lyrics) VALUES (?, ?, ?, ?)"
    crs.execute(comd, (uri, name, artists, lyrics))
    connection.commit()
    connection.close()
    return


def verify_database():
    """Creates the lyrics database if it doesn't exist"""
    connection = sql.connect("lyrics.db")
    crs = connection.cursor()
    crs.execute(
        "CREATE TABLE IF NOT EXISTS 'lyrics' (id text PRIMARY KEY, name text NOT NULL, artists text, lyrics text);")


def search_database(uri):
    """Return lyrics for a song from the database"""
    connection = sql.connect("lyrics.db")
    crs = connection.cursor()
    cmd = f"SELECT lyrics FROM lyrics WHERE id = ?"
    crs.execute(cmd, (uri,))
    result = crs.fetchall()
    crs.close()
    return result[0][0] if result else None


def search_genius(song):
    """Search genius.com for lyrics to a song

    Genius doesn't always return the right lyric as the first reult, especially with less popular songs.
    Some songs on Spotify have multiple artists listed and it's not always the first one who is credited as
    the author on Genius.
    """

    name = uniform_title(song['name'])
    artists = song['artists']
    first_artist = artists[0]['name']

    page = genius.search_song(name, first_artist)
    if not page:
        return None

    # Check if any of the listed artists and the song title more or less match the result.
    artist_match = any([(fuzz.ratio((page.artist).lower(), (artist['name']).lower()) > 70) for artist in artists])
    title_match = fuzz.partial_ratio((page.title).lower(), (name).lower()) > 70

    # In case the result seems off, ask the user.
    if not title_match or not artist_match:
        #  TODO: make this a popup window
        """
        print(
            f"Looked for lyrics for {name} by {artists[0]['name']}, but found only {page.title} by {page.artist}, use the lyric?")
        if input() not in ['y', 'yes', 'ye', 'yup']:
            return None
        """
        return None
    return remove_embed(page.lyrics)


