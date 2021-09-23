import spotipy
from PyQt6 import QtCore, QtGui, QtWidgets
from interface import UiMainWindow
import os
from lyrics import get_lyrics


def main():
    app = QtWidgets.QApplication([])
    ui = UiMainWindow()
    ui.show()
    app.exec()  # TODO: change lyrics automatically


if __name__ == "__main__" :
    main()
