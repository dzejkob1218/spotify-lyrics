from PyQt6.QtWidgets import QMainWindow
from threading import Timer
from helpers import *
from PyQt6 import QtCore, QtGui, QtWidgets
import spotipy
import sys
import lyrics
import lyricsgenius
import random
import time

sp = None
UPDATE_TIME = 5
IMG_DIR = 'cover.jpg'  # gets the directory of the cover
INFO_LABELS = {
    'energy': 'Energy',
    'valence': 'Valence',
    'danceability': 'Dance',
    'speechiness': 'Speech',
    'acousticness': 'Acoustic',
    'instrumentalness': 'Instrumental',
    'liveness': 'Live'
}

JAM_LABELS = {
    'key': 'Key',
    'signature': 'Signature',
    'tempo': 'Tempo'
}


class UiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Remembers a song after loading to prevent searching for the same lyrics many times
        self.currently_loaded = None

        # Initialize main window
        # self.win = main_window
        self.setWindowTitle("Spotify Lyrics")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)  # Stay on top by default
        self.setStyleSheet("background-color: rgb(0, 0, 0); color: white;")
        self.setFixedSize(860, 680)
        self.statusBar().hide()

        # Central widget
        # self.centralwidget = QtWidgets.QWidget(self)

        # Cover image
        self.cover = self.element_cover_image(self)

        # Song title
        self.title = QtWidgets.QLabel(self)
        self.title.setGeometry(QtCore.QRect(350, 5, 441, 41))
        self.title.setFont(self.set_font(18, 75))

        # Song artists
        self.artist = QtWidgets.QLabel(self)
        self.artist.setGeometry(QtCore.QRect(350, 42, 441, 31))
        self.artist.setFont(self.set_font(14, 75))

        # lyrics space
        self.lyrics = self.element_lyrics_area(self)

        # Update button
        self.element_update_button(self)

        # Info tab
        self.info, self.labels, self.values = self.element_labels(self, "Info", attributes=INFO_LABELS, position=10)
        # Composition tab
        self.jam, self.jam_labels, self.jam_values = self.element_labels(self, "Composition", attributes=JAM_LABELS,
                                                                         position=180)

        self.update_lyrics()

    def set_font(self, size=11, weight=50):
        """ Returns bold font to use in some of the elements """
        font = QtGui.QFont()
        font.setFamily("Segoe WP")
        font.setPointSize(size)
        font.setWeight(weight)
        return font

    def element_lyrics_area(self, parent):
        scroll_area = QtWidgets.QScrollArea(parent)
        scroll_area.setGeometry(QtCore.QRect(350, 75, 500, 599))
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QtWidgets.QWidget()
        scroll_area_content.setGeometry(QtCore.QRect(0, 0, 459, 599))
        vertical_layout = QtWidgets.QVBoxLayout(scroll_area_content)
        lyrics = self.element_lyrics(scroll_area_content)
        vertical_layout.addWidget(lyrics)
        scroll_area.setWidget(scroll_area_content)
        return lyrics

    def element_lyrics(self, parent):
        lyrics = QtWidgets.QLabel(parent)
        font = QtGui.QFont()
        lyrics.setFont(self.set_font())
        return lyrics

    def element_update_button(self, parent):
        button = QtWidgets.QPushButton(parent)
        button.setGeometry(QtCore.QRect(710, 45, 100, 24))
        button.clicked.connect(
            lambda: self.update_lyrics(force_update=True))  # call the update function when button is clicked
        button.setFont(self.set_font(11))
        button.setStyleSheet("background-color: rgb(127, 127, 127);")
        button.setText("Update")
        return button

    def element_cover_image(self, parent):
        cover = QtWidgets.QLabel(self)
        cover.setGeometry(QtCore.QRect(10, 10, 331, 331))
        cover.setScaledContents(True)
        return cover

    def element_labels(self, parent, name="Info", attributes=INFO_LABELS, position=10):
        # Info window
        element = QtWidgets.QTabWidget(parent)
        element.setGeometry(QtCore.QRect(position, 350, 165, 181))
        tab = QtWidgets.QWidget()
        labels, values = {}, {}
        offset = 0
        for attribute in attributes:
            # Label
            label = QtWidgets.QLabel(tab)
            label.setGeometry(QtCore.QRect(10, 10 + offset * 20, 100, 21))
            label.setFont(self.set_font(11))
            label.setText(attributes[attribute])
            labels[attribute] = label
            # Value
            value = QtWidgets.QLabel(tab)
            value.setGeometry(QtCore.QRect(120, 10 + offset * 20, 40, 21))
            value.setFont(self.set_font(11))
            values[attribute] = value
            offset += 1  # move to next line
        element.addTab(tab, name)
        return element, labels, values

    def update_lyrics(self, force_update=False):
        """
        Refreshes the window to display information about the currently playing track.

        Playback can either be returned through Spotify API or reading the title of the main Spotify window.
        In case of the API, additional image and information are shown.

        Automatically checks every given interval if the song has changed.
        Parameter 'force_update' overrides that check and is by the 'update' button.
        """

        song, is_api_connected = lyrics.get_playback()

        # Pressing the 'update' button always reloads a song, even if it's loaded already
        if not force_update:
            # Update lyrics every interval specified as UPDATE_TIME
            Timer(UPDATE_TIME, self.update_lyrics).start()
            # Check if the currently playing song is already loaded
            if song == self.currently_loaded:
                return None

        # If the song has changed, remember it
        print("Update Called")
        self.currently_loaded = song

        # Load track features and track image from Spotify API
        if song and is_api_connected:
            lyrics.download_cover(song)
            features = lyrics.get_features(song)
            lyrics_text = lyrics.get_lyrics(song)

            self.toggle_details(True)  # Make sure everything is enabled
            self.cover.setPixmap(QtGui.QPixmap(IMG_DIR))  # Change the image
            self.set_song(song, lyrics_text)  # Change text
            self.set_labels(features)

        # If the API isn't working, show just the title, artist and lyrics
        elif song and not is_api_connected:
            lyrics_text = lyrics.get_lyrics(song)
            self.toggle_details(False)
            self.set_song(song, lyrics_text)

        # If no song was found, hide everything
        else:
            self.toggle_details(False)
            self.title.setText('')  # change title and artist
            self.artist.setText('')
            self.lyrics.setText('Nothing playing')
            for label in INFO_LABELS:
                self.values[label].setText("")

    def set_song(self, song, lyrics_text):
        """ Sets name, artists and lyrics of current song """
        self.title.setText(song['name'])  # change title and artist
        self.artist.setText(parse_artists(song['artists']))
        self.lyrics.setText(lyrics_text)

    def set_labels(self, features):
        # Set values in info
        for label in INFO_LABELS:
            value = features[label]
            color = color_from_value(value)
            score = format_value(value)
            content = f"<html><head/><body><p><span style=\" color:{color};\">{score}%</span></p></body></html>"
            self.values[label].setText(content)
        # Set values in composition
        for label in JAM_LABELS:
            value = format_composition(label, features)
            self.jam_values[label].setText(value)

    def toggle_details(self, toggle):
        """ Hides or shows all elements that need Spotify API to load """
        self.info.setEnabled(toggle)
        self.jam.setEnabled(toggle)
        self.cover.setEnabled(toggle)
