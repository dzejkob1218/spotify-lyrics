import spotipy
from PyQt5 import QtCore, QtGui, QtWidgets
from interface import UiMainWindow
import os
from lyrics import get_lyrics
from spotipy import Spotify, SpotifyOAuth, util, CacheFileHandler
from dotenv import load_dotenv
load_dotenv()

cache_handler = CacheFileHandler(cache_path="")
auth_manager = SpotifyOAuth(scope='user-read-playback-state', cache_handler=cache_handler)
sp = Spotify(auth_manager=auth_manager)

def main():
    app = QtWidgets.QApplication([])
    ui = UiMainWindow(sp)
    ui.show()
    app.exec()

if __name__ == "__main__" :
    main()
