# -*- coding: UTF-8 -*-

import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox, QToolBar, QToolButton, QStackedLayout
from PyQt5.QtCore import Qt
from qt_material import QtStyleTools
from bookmark import Bookmark

class App(QtWidgets.QMainWindow, QtStyleTools):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.apply_stylesheet(self, 'dark_teal.xml', extra= {'font_family': 'Microsoft YaHei'})
        self.setup()

    def setup(self):
        # 添加侧边栏
        toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, toolBar)
        # 添加主页
        bookmarkBtn = self.createButton("书签工具")
        bookmarkBtn.clicked.connect(lambda: self.onButtonClicked(0))
        toolBar.addWidget(bookmarkBtn)


        mainWidget = QWidget(self)
        self.mainLayout = QStackedLayout(mainWidget)

        # 设置页面模块
        self.mainLayout.addWidget(self.bookmarkUI())

        mainWidget.setLayout(self.mainLayout)
        # 设置中心窗口
        self.setCentralWidget(mainWidget)

    def createButton(self, text):
        btn = QToolButton(self)
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        return btn

    def onButtonClicked(self, index):
        if index < self.mainLayout.count():
            self.mainLayout.setCurrentIndex(index)

    def closeEvent(self, event):
        reply = QMessageBox.warning(
            self, 
            '警告',"是否确定退出程序？", 
            QMessageBox.Yes |QMessageBox.No, QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            time.sleep(0.3)
            event.accept()
        else:
            event.ignore()

    def bookmarkUI(self):
        self.bookmark = Bookmark(self)
        return self.bookmark
