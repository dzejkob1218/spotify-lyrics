from PyQt5.QtWidgets import QMainWindow
from threading import Timer
from helpers import *
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtGui import QDesktopServices

import spotipy
import sys
import lyrics
import lyricsgenius
import random
import time
import vote
from config import PROCESSING_ID, FAV_ID, STAR_ID, LEGACY_ID

sp = None
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
    def __init__(self, sp):
        super().__init__()

        self.sp = sp

        # Remembers a song after loading to prevent searching for the same lyrics many times
        self.currently_loaded = None

        # Initialize main window
        # self.win = main_window
        self.setWindowTitle("Spotify Lyrics")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)  # Stay on top by default
        self.setStyleSheet("""background-color: rgb(0, 0, 0); color: white;""")
        self.setFixedSize(860, 680)
        self.statusBar().hide()

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

        # voting space
        self.voting = self.element_voting_area(self)

        # Playlist names display
        self.playlist_labels = self.create_playlist_labels()
        self.load_playlist_names()

        # Update button
        self.element_button(self, (750, 45, 100, 24), "Update", function=lambda: self.update_lyrics(force_update=True))

        # Voting buttons - evenly spaced
        button_width = 100
        button_height = 30
        spacing = 20
        start_x = 50

        self.element_button(self.voting, (start_x, 200, button_width, button_height), "Fav ↑", function=lambda: self.handle_vote('fav'))
        self.element_button(self.voting, (start_x + button_width + spacing, 200, button_width, button_height), "Keep →", function=lambda: self.handle_vote('keep'))
        self.element_button(self.voting, (start_x + (button_width + spacing) * 2, 200, button_width, button_height), "Delete ↓", function=lambda: self.handle_vote('delete'))
        self.element_button(self.voting, (start_x + (button_width + spacing) * 3, 200, button_width, button_height), "Skip ←", function=lambda: self.handle_vote('skip'))

        # Info tab
        self.info, self.labels, self.values = self.element_labels(self, "Info", attributes=INFO_LABELS, position=10)
        # Composition tab
        self.jam, self.jam_labels, self.jam_values = self.element_labels(self, "Composition", attributes=JAM_LABELS,
                                                                         position=180)
        self.update_lyrics()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for voting"""
        key = event.key()
        if key == QtCore.Qt.Key.Key_Up:
            self.handle_vote('fav')
        elif key == QtCore.Qt.Key.Key_Right:
            self.handle_vote('keep')
        elif key == QtCore.Qt.Key.Key_Down:
            self.handle_vote('delete')
        elif key == QtCore.Qt.Key.Key_Left:
            self.handle_vote('skip')

    def handle_vote(self, action):
        """Handle voting actions by passing current track URI to vote functions"""
        if not self.currently_loaded:
            print("ERROR: No track loaded")
            return

        track_uri = self.currently_loaded.get('uri')
        if action == 'fav':
            vote.fav(self.sp, track_uri)
        elif action == 'keep':
            vote.keep(self.sp, track_uri)
        elif action == 'delete':
            vote.delete(self.sp, track_uri)
        elif action == 'skip':
            vote.skip(self.sp, track_uri)

    def create_playlist_labels(self):
        """Create labels to display playlist names"""
        labels = {}
        y_position = 20
        line_height = 25

        # Processing playlist
        processing_label = QtWidgets.QLabel(self.voting)
        processing_label.setGeometry(QtCore.QRect(20, y_position, 460, 20))
        processing_label.setFont(self.set_font(10, 50))
        labels['processing'] = processing_label

        # Favorites playlist
        fav_label = QtWidgets.QLabel(self.voting)
        fav_label.setGeometry(QtCore.QRect(20, y_position + line_height, 460, 20))
        fav_label.setFont(self.set_font(10, 50))
        labels['fav'] = fav_label

        # Star playlist
        star_label = QtWidgets.QLabel(self.voting)
        star_label.setGeometry(QtCore.QRect(20, y_position + line_height * 2, 460, 20))
        star_label.setFont(self.set_font(10, 50))
        labels['star'] = star_label

        # Legacy playlist
        legacy_label = QtWidgets.QLabel(self.voting)
        legacy_label.setGeometry(QtCore.QRect(20, y_position + line_height * 3, 460, 20))
        legacy_label.setFont(self.set_font(10, 50))
        labels['legacy'] = legacy_label

        return labels

    def load_playlist_names(self):
        """Fetch and display playlist names from Spotify"""
        try:
            if PROCESSING_ID:
                playlist = self.sp.playlist(PROCESSING_ID, fields='name')
                self.playlist_labels['processing'].setText(f"Processing: {playlist['name']}")
            else:
                self.playlist_labels['processing'].setText("Processing: Not set")

            if FAV_ID:
                playlist = self.sp.playlist(FAV_ID, fields='name')
                self.playlist_labels['fav'].setText(f"Favorites: {playlist['name']}")
            else:
                self.playlist_labels['fav'].setText("Favorites: Not set")

            if STAR_ID:
                playlist = self.sp.playlist(STAR_ID, fields='name')
                self.playlist_labels['star'].setText(f"Star: {playlist['name']}")
            else:
                self.playlist_labels['star'].setText("Star: Not set")

            if LEGACY_ID:
                playlist = self.sp.playlist(LEGACY_ID, fields='name')
                self.playlist_labels['legacy'].setText(f"Legacy: {playlist['name']}")
            else:
                self.playlist_labels['legacy'].setText("Legacy: Not set")
        except Exception as e:
            print(f"Error loading playlist names: {e}")
            self.playlist_labels['processing'].setText("Processing: Error loading")
            self.playlist_labels['fav'].setText("Favorites: Error loading")
            self.playlist_labels['star'].setText("Star: Error loading")
            self.playlist_labels['legacy'].setText("Legacy: Error loading")

    def set_font(self, size=11, weight=50):
        """ Returns bold font to use in some of the elements """
        font = QtGui.QFont()
        font.setFamily("Segoe WP")
        font.setPointSize(size)
        font.setWeight(weight)
        return font

    def element_voting_area(self, parent):
        scroll_area = QtWidgets.QTabWidget(parent)
        scroll_area.setGeometry(QtCore.QRect(350, 75, 500, 599))
        #scroll_area.setWidgetResizable(True)
        #croll_area_content = QtWidgets.QWidget()
        #scroll_area_content.setGeometry(QtCore.QRect(0, 0, 459, 599))
        #vertical_layout = QtWidgets.QVBoxLayout(scroll_area_content)
        #lyrics_text = self.element_lyrics(scroll_area_content)
        #lyrics_text.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        #vertical_layout.addWidget(lyrics_text)
        #scroll_area.setWidget(scroll_area_content)
        #return lyrics_text
        return scroll_area


    def element_button(self, parent, position, label, function):
        button = QtWidgets.QPushButton(parent)
        button.setGeometry(QtCore.QRect(*position))
        button.clicked.connect(function)  # call the update function when button is clicked
        button.setFont(self.set_font(11))
        button.setStyleSheet("background-color: rgb(127, 127, 127);")
        button.setText(label)
        return button

    def element_cover_image(self, parent):
        cover = QtWidgets.QLabel(self)
        cover.setGeometry(QtCore.QRect(10, 10, 331, 331))
        cover.setScaledContents(True)
        return cover

    def element_labels(self, parent, name="Info", attributes=INFO_LABELS, position=10):
        # Info window
        element = QtWidgets.QTabWidget(parent)
        element.setStyleSheet("color: grey;")
        element.setGeometry(QtCore.QRect(position, 350, 165, 181))
        tab = QtWidgets.QWidget()
        tab.setStyleSheet("color: white;")
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
        # TODO: When updating after there was no playback the app crashes
        song = lyrics.get_playback(self.sp)

        # If the song has changed, remember it
        print("Update Called")
        self.currently_loaded = song
        if song:
            lyrics.download_cover(song)
            features = lyrics.get_features(song, self.sp)
            lyrics_text = lyrics.get_lyrics(song)

            self.toggle_details(True)  # Make sure everything is enabled
            self.cover.setPixmap(QtGui.QPixmap(IMG_DIR))  # Change the image

            def open_image(event):
                QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(IMG_DIR))

            self.cover.mousePressEvent = open_image
            self.set_song(song, lyrics_text)  # Change text
            self.set_labels(features)

        # If no song was found, hide everything
        else:
            print("No song")
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
        if toggle:
            self.info.show()
            self.jam.show()
            self.cover.show()
        else:
            self.info.hide()
            self.jam.hide()
            self.cover.hide()