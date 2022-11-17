# -*- coding: UTF-8 -*-
import os
import sys
import tkinter as tk

from PyQt5 import QtWidgets, QtGui

from app import App

def dpi():
    # 适配4K分辨率
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    d = '96'
    if w >= 2560 and h > 1080:
        d = '128'
    root.destroy()
    return d

def main():
    # pdf_handler = MyPDFHandler(u'/home/vincent/下载/现代数学手册(3)计算机数学卷.pdf', mode = mode.COPY)
    # pdf_handler.add_bookmarks_by_read_txt('./test2.txt')
    # pdf_handler.save2file(u'现代数学手册(3)计算机数学卷-目录书签版.pdf')
    os.environ["QT_FONT_DPI"] = dpi()
    qtApp = QtWidgets.QApplication(sys.argv)
    qtApp.setWindowIcon(QtGui.QIcon("app.ico"))
    
    # 创建主窗口
    ui = App()
    # 设置窗口标题
    ui.setWindowTitle("PDF工具")
    # 设置主窗口初始大小
    screen = QtWidgets.QApplication.primaryScreen()
    size = screen.size()
    ui.resize(int(size.width() * 0.5), int(size.height() * 0.5))
    # 显示界面
    ui.show()
    # 进入界面循环
    sys.exit(qtApp.exec())


if __name__ == '__main__':
    main()