# -*- coding: UTF-8 -*-

from PyQt5.QtWidgets import QMessageBox

# 只有ok确认按钮的消息框
def MsgboxOk(parent, title: str, text: str):
    msgBox = QMessageBox(parent)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.exec()