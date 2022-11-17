# -*- coding: UTF-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QFileDialog,
    QComboBox
)

from controls.MyLineEdit import MyLineEdit
from controls.messagebox import MsgboxOk
from sdk.pdf import PDFHandleMode, PDFHandler

class Bookmark(QWidget):
    def __init__(self, parent=None):
        super(Bookmark, self).__init__(parent)
        self.ui()

    def ui(self):
        layout = QVBoxLayout()

        settingsLayout = QHBoxLayout()
        settingLeftLayout = QFormLayout()
        settingRightLayout = QFormLayout()

        self.pdfFileEdit = MyLineEdit()
        self.txtFileEdit = MyLineEdit()
        self.pdfModeCmbx = QComboBox()
        self.pdfModeCmbx.addItems(['追加', '清空'])

        # 左
        settingLeftLayout.addRow("PDF文件", self.pdfFileEdit)
        # 右
        settingRightLayout.addRow("Txt文件", self.txtFileEdit)
        settingRightLayout.addRow("操作模式", self.pdfModeCmbx)

        opLayout = QHBoxLayout()

        self.importBtn = QPushButton("导入书签")
        self.exportBtn = QPushButton("导出书签")

        opLayout.addStretch(1)
        opLayout.addWidget(self.exportBtn)
        opLayout.addWidget(self.importBtn)

        settingsLayout.addLayout(settingLeftLayout, 1)
        settingsLayout.addLayout(settingRightLayout, 1)
        layout.addLayout(settingsLayout)
        layout.addLayout(opLayout)

        self.setLayout(layout)

        self.pdfFileEdit.mousePressed.connect(self.onClickPdfFile)
        self.txtFileEdit.mousePressed.connect(self.onClickTxtFile)
        self.importBtn.clicked.connect(self.importBookmarks)
        self.exportBtn.clicked.connect(self.exportBookmarks)

    def onClickPdfFile(self):
        self.pdfFile = self.selectPdfFile()
        self.pdfFileEdit.setText(self.pdfFile)

    def onClickTxtFile(self):
        self.txtFile = self.selectTxtFile()
        self.txtFileEdit.setText(self.txtFile)

    def fromSettings(self):
        self.txtFile = self.txtFileEdit.text()
        self.pdfFile = self.pdfFileEdit.text()
        self.pdfMode = self.pdfModeCmbx.currentText()

    def importBookmarks(self):
        self.fromSettings()
        if self.pdfFile == '' or self.txtFile == '':
            return

        if self.pdfMode == '追加':
            mode = PDFHandleMode.COPY
        elif self.pdfMode == '清空':
            mode = PDFHandleMode.NEWLY

        pdf = PDFHandler(self.pdfFile, mode)
        pdf.addBookmarksByReadTxt(self.txtFile)
        pdf.save2file(pdf.fileName + "_目录书签版.pdf")
        MsgboxOk(self, "成功", "添加书签成功!")
    
    def exportBookmarks(self):
        self.fromSettings()
        if self.pdfFile == '':
            return

        pdf = PDFHandler(self.pdfFile, PDFHandleMode.COPY)
        pdf.bookmarks2Txt()
        MsgboxOk(self, "成功", "导出书签成功!")

    def selectPdfFile(self):
        file, filetype = QFileDialog.getOpenFileName(self,  "选取文件", "./", "Text Files (*.pdf)") 
        return file

    def selectTxtFile(self):
        file, filetype = QFileDialog.getOpenFileName(self,  "选取文件", "./", "Text Files (*.txt)") 
        return file