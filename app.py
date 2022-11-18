# -*- coding: UTF-8 -*-

import time
from qt_material import QtStyleTools
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox, QToolBar, QToolButton, QStackedLayout
from PyQt5.QtCore import Qt
from bookmark import Bookmark
from spliter import Spliter

class App(QtWidgets.QMainWindow, QtStyleTools):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.apply_stylesheet(self, 'dark_teal.xml', extra= {'font_family': 'Microsoft YaHei'})
        self.setup()

    def setup(self):
        # 添加侧边栏
        toolBar = QToolBar(self)
        self.addToolBar(Qt.LeftToolBarArea, toolBar)
        # 添加书签工具页面
        bookmarkBtn = self.createButton("书签工具")
        bookmarkBtn.clicked.connect(lambda: self.onButtonClicked(0))
        toolBar.addWidget(bookmarkBtn)

        # 添加分割工具页面
        spliterBtn = self.createButton("分页工具")
        spliterBtn.clicked.connect(lambda: self.onButtonClicked(1))
        toolBar.addWidget(spliterBtn)

        mainWidget = QWidget(self)
        self.mainLayout = QStackedLayout(mainWidget)

        # 设置页面模块
        self.mainLayout.addWidget(self.bookmarkUI())
        self.mainLayout.addWidget(self.spliterUI())

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

    def spliterUI(self):
        self.spliter = Spliter(self)
        return self.spliter
    
