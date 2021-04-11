import spotipy
from PyQt5 import QtCore, QtGui, QtWidgets
from interface import Ui_MainWindow
import os


def main():
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Spotify Lyrics")
    ui = Ui_MainWindow()
    ui.render(win)
    win.show()
    app.exec()  # TODO: change lyrics automatically