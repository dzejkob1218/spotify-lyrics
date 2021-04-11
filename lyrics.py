import lyricsgenius
import spotipy
import requests
from fuzzywuzzy import fuzz
import sqlite3 as sql
import re
from dotenv import load_dotenv
import os

load_dotenv()


# TODO - find a way for users to add their own credentials
username = os.environ.get("")
TOKEN = spotipy.Spotify(
        auth=spotipy.util.prompt_for_user_token(username, 'user-read-playback-state',
                                                client_id=os.environ.get("spotify_client_id"),
                                                client_secret=os.environ.get("spotify_client_secret"),
                                                redirect_uri='http://localhost:8080'))
genius = lyricsgenius.Genius(os.environ.get("genius-secret"))


def get_lyrics():
    """Look for the lyrics either in the database or on genius.com"""

    spotify = spotipy.Spotify(TOKEN)
    song = spotify.current_playback()['item']  # this shouldn't be here
    uri = song['uri']
    features = spotify.audio_features(uri)
    download_cover(song)

    db_result = search_database(uri)
    if db_result:
        print("Getting lyrics from database")
        return db_result

    genius_result = search_genius(song)
    if genius_result:
        print("Lyrics found on Genius - adding to database")
        addLyrics(uri, genius_result)
        return genius_result

    print("Lyrics not found")
    return None


def download_cover(song):
    """Saves the cover of song being played to cover.jpg"""
    cover = song['album']['images'][0]['url']
    img = requests.get(cover).content
    with open('cover.jpg', 'wb') as handler:
        handler.write(img)


def addLyrics(uri, lyrics):
    """Adds new lyrics to the database along with the song uri"""
    connection = sql.connect("lyrics.db")
    crs = connection.cursor()
    comd = "INSERT INTO lyrics (id, lyrics) VALUES (?,?)"
    crs.execute(comd, (uri, lyrics))
    connection.commit()
    connection.close()
    return


def search_database(uri):
    """Return lyrics for a song from the database"""
    connection = sql.connect("lyrics.db")
    crs = connection.cursor()
    cmd = f"SELECT lyrics FROM lyrics WHERE uri = ?"
    crs.execute(cmd, uri)
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
    title_match = fuzz.partial_ratio((page.title).lower(),(name).lower()) > 70

    # In case the result seems off, ask the user.
    if not title_match or not artist_match:
        #  TODO: make this a popup window
        print(f"Looked for lyrics for {name} by {artists[0]['name']}, but found only {page.title} by {page.artist}, use the lyric?")
        if input() not in ['y', 'yes', 'ye', 'yup']:
            return None
    return page.lyrics


def uniform_title(title):
    """Does the best it can to get the actual song title from whatever the name of the track is

    Track names on Spotify are riddled with information on remixes, remasters, features, live versions etc.
    This function tries to remove these, but it might not work in every case, especially in languages other
    than English since it works by looking for keywords
    """
    keywords = ['remaster', 'delux', 'from', 'mix', 'version', 'edit', 'live', 'track', 'session', 'extend', 'feat', 'studio']
    if not any(keyword in title.lower() for keyword in keywords):
        return title

    newtitle = title
    #  uses split to remove - everything after hyphen if there's a keyword there
    #  (doesn't separate ones without spaces since some titles are like-this)
    if ' - ' in newtitle:
        newtitle = newtitle.split(" - ", 1)
        if any(keyword in newtitle[1].lower() for keyword in keywords):
            newtitle = newtitle[0]

    # removes everything in parentheses if there's a keyword inside
    if '(' in newtitle:
        regex = re.compile(".*?\((.*?)\)")
        result = re.findall(regex, title)
        if len(result) > 0:
            if any(keyword in result[0].lower() for keyword in keywords):
                tag = '(' + result[0] + ')'
                newtitle = newtitle.replace(tag, '')

    newtitle = newtitle.strip()
    return newtitle

