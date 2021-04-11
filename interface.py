from PyQt5 import QtCore, QtGui, QtWidgets
import spotipy
import sys
import lyrics as info
import lyricsgenius
import random
import time


sp = None
img_dir = 'cover.jpg' # gets the directory of the cover


class Ui_MainWindow(object):
    def render(self, MainWindow): # TODO: Why can't this be init?
        self.win = MainWindow
        MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(820, 680)
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);\n", "color: white;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.cover = QtWidgets.QLabel(self.centralwidget)
        self.cover.setGeometry(QtCore.QRect(10, 10, 331, 331))
        self.cover.setText("")
        self.cover.setPixmap(QtGui.QPixmap("../../cover.jpg"))
        self.cover.setScaledContents(True)
        self.cover.setObjectName("cover")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(350, 0, 441, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe WP")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.artist = QtWidgets.QLabel(self.centralwidget)
        self.artist.setGeometry(QtCore.QRect(350, 37, 441, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe WP")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.artist.setFont(font)
        self.artist.setObjectName("artist")

        # lyrics space
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(350, 70, 461, 561))

        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 459, 559))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        # lyrics
        self.lyrics = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lyrics.setFont(font)
        self.lyrics.setObjectName("lyrics")
        self.lyrics.setAlignment(QtCore.Qt.AlignTop)  # aligns the lyrics to the top
        self.verticalLayout.addWidget(self.lyrics)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # karaoke button
        self.mode = False
        self.karaoke = QtWidgets.QPushButton(self.centralwidget)
        self.karaoke.setGeometry(QtCore.QRect(735, 30, 75, 20))
        self.karaoke.clicked.connect(self.karaoke_mode) # call the update function when button is clicked
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.karaoke.setFont(font)
        self.karaoke.setStyleSheet("background-color: rgb(127, 127, 127);")
        self.karaoke.setObjectName("karaoke")


        # update button
        self.update = QtWidgets.QPushButton(self.centralwidget)
        self.update.setGeometry(QtCore.QRect(735, 0, 75, 20))
        self.update.clicked.connect(self.updateLyrics) # call the update function when button is clicked
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.update.setFont(font)
        self.update.setStyleSheet("background-color: rgb(127, 127, 127);")
        self.update.setObjectName("update")

        ####
        self.info = QtWidgets.QTabWidget(self.centralwidget)
        self.info.setGeometry(QtCore.QRect(10, 350, 330, 281))
        self.info.setObjectName("info")
        self.stats = QtWidgets.QWidget()
        self.stats.setObjectName("stats")
        self.dance_label = QtWidgets.QLabel(self.stats)
        self.dance_label.setGeometry(QtCore.QRect(10, 50, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.dance_label.setFont(font)
        self.dance_label.setObjectName("dance_label")
        self.valence_label = QtWidgets.QLabel(self.stats)
        self.valence_label.setGeometry(QtCore.QRect(10, 30, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.valence_label.setFont(font)
        self.valence_label.setObjectName("valence_label")
        self.energy_label = QtWidgets.QLabel(self.stats)
        self.energy_label.setGeometry(QtCore.QRect(10, 10, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.energy_label.setFont(font)
        self.energy_label.setObjectName("energy_label")
        self.dance_score = QtWidgets.QLabel(self.stats)
        self.dance_score.setGeometry(QtCore.QRect(80, 50, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.dance_score.setFont(font)
        self.dance_score.setObjectName("dance_score")
        self.valence_score = QtWidgets.QLabel(self.stats)
        self.valence_score.setGeometry(QtCore.QRect(80, 30, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.valence_score.setFont(font)
        self.valence_score.setObjectName("valence_score")
        self.energy_score = QtWidgets.QLabel(self.stats)
        self.energy_score.setGeometry(QtCore.QRect(80, 10, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.energy_score.setFont(font)
        self.energy_score.setObjectName("energy_score")
        self.info.addTab(self.stats, "")
        self.jam = QtWidgets.QWidget()
        self.jam.setObjectName("jam")
        self.info.addTab(self.jam, "")
        ####
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuTest = QtWidgets.QMenu(self.menubar)
        self.menuTest.setObjectName("menuTest")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionTest = QtWidgets.QAction(MainWindow)
        self.actionTest.setObjectName("actionTest")
        self.menuTest.addAction(self.actionTest)
        self.menubar.addAction(self.menuTest.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.updateLyrics()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate  # TODO: what is this for if changing text works without _translate?
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "Title"))
        self.artist.setText(_translate("MainWindow", "Artist"))
        self.lyrics.setText(_translate("MainWindow", "lyrics not found"))
        self.update.setText(_translate("MainWindow", "Update"))
        self.karaoke.setText(_translate("MainWindow", "Karaoke"))
        self.dance_label.setText(_translate("MainWindow", "Dance:"))
        self.valence_label.setText(_translate("MainWindow", "Valence:"))
        self.energy_label.setText(_translate("MainWindow", "Energy:"))
        self.dance_score.setText(_translate("MainWindow", "8.3"))
        self.valence_score.setText(_translate("MainWindow", "8.3"))
        self.energy_score.setText(_translate("MainWindow", "8.3"))
        self.info.setTabText(self.info.indexOf(self.stats), _translate("MainWindow", "Tab 1"))
        self.info.setTabText(self.info.indexOf(self.jam), _translate("MainWindow", "Tab 2"))
        self.menuTest.setTitle(_translate("MainWindow", "Test"))
        self.actionTest.setText(_translate("MainWindow", "Test"))

    def karaoke_mode(self):
        if self.mode:
            self.mode = False
            self.win.showNormal()
            self.lyrics_size(11)
            self.scrollArea.setGeometry(QtCore.QRect(350, 70, 1200, 900))
            self.karaoke.setText("Karaoke")
        else:
            self.mode = True        # TODO: add auto scroll to karaoke mode
            self.win.showMaximized()
            self.lyrics_size(25)
            self.scrollArea.setGeometry(QtCore.QRect(350, 70, 1200, 900))
            self.karaoke.setText("Normal")

    def lyrics_size(self, size):
        new_font = self.lyrics.font()
        new_font.setPointSize(size)
        self.lyrics.setFont(new_font)

    def updateLyrics(self):
        # TODO: How to get all the data here?
        print("Update Called")
        lyr = info.get_lyrics()
        _translate = QtCore.QCoreApplication.translate
        self.cover.setPixmap(QtGui.QPixmap(img_dir)) # change the image
        self.title.setText(_translate("MainWindow",cur['name'])) # change title and artist
        self.artist.setText(_translate("MainWindow",cur['artists'][0]['name']))
        self.lyrics.setText(_translate("MainWindow",lyr))
        energy = f"<html><head/><body><p><span style=\" color:{info.valToColor(features[0]['energy'])};\">{info.valToScore(features[0]['energy'])}</span></p></body></html>"
        dance = f"<html><head/><body><p><span style=\" color:{info.valToColor(features[0]['danceability'])};\">{info.valToScore(features[0]['danceability'])}</span></p></body></html>"
        valence = f"<html><head/><body><p><span style=\" color:{info.valToColor(features[0]['valence'])};\">{info.valToScore(features[0]['valence'])}</span></p></body></html>"
        self.dance_score.setText(_translate("MainWindow", dance))
        self.valence_score.setText(_translate("MainWindow", valence))
        self.energy_score.setText(_translate("MainWindow", energy))
        #self.lyrics.setText(_translate("MainWindow", f"<html><head/><body><p><span style=\" color:#ffffff;\">{lyr}</span></p></body></html>"))
