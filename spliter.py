# -*- coding: UTF-8 -*-
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QFileDialog,
    QComboBox, QLineEdit
)

from controls.MyLineEdit import MyLineEdit
from controls.messagebox import MsgboxOk
from sdk.pdf import PDFHandleMode, PDFHandler


class Spliter(QWidget):
    def __init__(self, parent=None):
        super(Spliter, self).__init__(parent)
        self.ui()

    def ui(self):
        layout = QVBoxLayout()

        settingsLayout = QHBoxLayout()
        settingLeftLayout = QFormLayout()
        settingRightLayout = QFormLayout()

        self.pdfFileEdit = MyLineEdit()
        self.splitPageEdit = QLineEdit()

        # 左
        settingLeftLayout.addRow("PDF文件", self.pdfFileEdit)

        # 右
        settingRightLayout.addRow("分割定义", self.splitPageEdit)

        opLayout = QHBoxLayout()
        self.startBtn = QPushButton("开始")

        opLayout.addStretch(1)
        opLayout.addWidget(self.startBtn)

        settingsLayout.addLayout(settingLeftLayout, 1)
        settingsLayout.addLayout(settingRightLayout, 1)
        layout.addLayout(settingsLayout)
        layout.addLayout(opLayout)
        self.setLayout(layout)

        self.pdfFileEdit.mousePressed.connect(self.onClickPdfFile)
        self.startBtn.clicked.connect(self.start)

    def start(self):
        self.process(self.splitPageEdit.text())
        MsgboxOk(self, "成功", "PDF分割完成!")

    def process(self, pages:str):
        # 1,3,5-7,8-10,10-81
        try:
            pdf = PDFHandler(self.pdfFileEdit.text(), PDFHandleMode.NONE)
            p = pages.split(",")
            for stage in p:
                p2 = stage.split("-")
                if len(p2) == 0:
                    continue
                elif len(p2) == 1:
                    start = int(p2[0])
                    pdf.split2File(start, start)
                else: # 大于1的
                    start = int(p2[0])
                    end = int(p2[1])
                    pdf.split2File(start, end)

        except Exception as msg:
            MsgboxOk(self, "错误", str(msg))
            return

    def onClickPdfFile(self):
        self.pdfFile = self.selectPdfFile()
        self.pdfFileEdit.setText(self.pdfFile)

    def selectPdfFile(self):
        file, filetype = QFileDialog.getOpenFileName(self,  "选取文件", "./", "Text Files (*.pdf)") 
        return file