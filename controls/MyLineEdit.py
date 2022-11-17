# -*- coding: UTF-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLineEdit

class MyLineEdit(QLineEdit):
    mousePressed = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        self.mousePressed.emit()