# -*- coding: UTF-8 -*-
import os
from typing import List
from io import BytesIO
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger

title_8space = "    "
title_2 = title_8space
title_3 = title_2 + title_8space
title_4 = title_3 + title_8space

class PDFHandleMode(object):
    '''
    处理PDF文件的模式
    '''
    # 保留源PDF文件的所有内容和信息，在此基础上修改
    COPY = 'copy'
    # 仅保留源PDF文件的页面内容，在此基础上修改
    NEWLY = 'newly'
    # 什么都不做
    NONE = 'none'

class Tree:
    def __init__(self, title: str, page: str, children = []):
        self.title: str = title.lstrip()
        self.page: int = int(page)
        self.children: List[Tree] = children

class PDFHandler(object):

    def __init__(self, filePath: str, mode = PDFHandleMode.NONE):
        self.reader = PdfFileReader(filePath)
        self.fileName = os.path.basename(filePath)[0:-4]
        self.pagesNum = self.reader.getNumPages()

        # 可写的PDF对象，根据不同的模式进行初始化
        self.writer = PdfFileWriter()
        if mode == PDFHandleMode.COPY:
            for page in self.reader.pages:
                self.writer.add_page(page)

            bookmarks = self.getAllBookmarks(self.reader)
            self.addBookmarks(self.writer, bookmarks)
            
        elif mode == PDFHandleMode.NEWLY:
            for idx in range(self.pagesNum):
                page = self.reader.getPage(idx)
                self.writer.insertPage(page, idx)
    

    @staticmethod
    def split(pdf: PdfFileReader, start: int, end: int):
        pdfWriter = PdfFileWriter()
        for idx in range(start-1, end):
            page = pdf.getPage(idx)
            pdfWriter.insertPage(page, idx-(start-1))
        
        # 因为分割了，所以页码会发生变化
        # if len(bookmarks) == 0:
        #     bookmarks = PDFHandler.getAllBookmarks(pdf)
        # rangeBookmarks = PDFHandler.getBookmarksByPage(bookmarks, start, end, repage=True)
        # PDFHandler.addBookmarks(pdfWriter, rangeBookmarks)
        return pdfWriter

    @staticmethod
    def merge(filePaths: list, keepBookmarks = True):
        merger = PdfFileMerger()
        for filePath in filePaths:
            merger.append(open(filePath, 'rb'))
        
        bio = BytesIO()
        merger.write(bio)
        merger.close()
        writer = PdfFileWriter(bio)

        if keepBookmarks:
            curPages = 0
            for filePath in filePaths:
                pdf = PdfFileReader(filePath)
                bookmarks = PDFHandler.getAllBookmarks(pdf)
                PDFHandler.offsetBookmarksPage(bookmarks, curPages)
                curPages = pdf.getNumPages()
                PDFHandler.addBookmarks(writer, bookmarks)
        
        return writer

    @staticmethod
    def bookmarks2Txt(bookmarks: List[Tree], fileName: str):
        with open(fileName, "w", encoding='utf-8') as f:
            for item in bookmarks:
                f.write(PDFHandler.tree2BookmarkTxt(item, 1))
                for item2 in item.children:
                    f.write(PDFHandler.tree2BookmarkTxt(item2, 2))
                    for item3 in item2.children:
                        f.write(PDFHandler.tree2BookmarkTxt(item3, 3))
                        for item4 in item3.children:
                            f.write(PDFHandler.tree2BookmarkTxt(item4, 4))
    
    @staticmethod
    def readBookmarksFromTxt(txtFilePath: str):
        bookmarks: List[Tree] = []
        with open(txtFilePath,'r', encoding='UTF-8') as fin:
            for line in fin:
                line = line.replace("\t","    ") # 替换tab为4个空格

                line = line.rstrip()
                if not line:
                    continue

                try:
                    title = line.split('@')[0].rstrip()
                    page = line.split('@')[1].strip()

                    if (not title) or (not page):
                        continue

                    if title.startswith(title_4): # 4级
                        parent1 = bookmarks[-1]
                        parent2 = parent1.children[-1] # 取出2级
                        parent3 = parent2.children[-1] # 取出3级
                        tmp = Tree(title, page, [])
                        parent3.children.append(tmp)

                    elif title.startswith(title_3): # 3级
                        parent1 = bookmarks[-1]
                        parent2 = parent1.children[-1] # 取出2级
                        tmp = Tree(title, page, [])
                        parent2.children.append(tmp)

                    elif title.startswith(title_2): # 2级
                        parent1 = bookmarks[-1]
                        tmp = Tree(title, page, [])
                        parent1.children.append(tmp)
                    else: # 1级
                        tmp = Tree(title, page, [])
                        bookmarks.append(tmp)
                    
                except Exception as msg:
                    print(msg)
                    continue
        return bookmarks

    @staticmethod
    def tree2BookmarkTxt(item: Tree, level: int):
        if level == 1:
            space = ""
        elif level == 2:
            space = title_2
        elif level == 3:
            space = title_3
        elif level == 4:
            space = title_4
        
        title = item.title
        return space + title + "@" + str(item.page) + "\n"

    @staticmethod
    def offsetBookmarksPage(bookmarks: List[Tree], offset: int):
        for bm in bookmarks:
            bm.page = bm.page - offset
            if len(bm.children) > 0:
                PDFHandler.offsetBookmarksPage(bm.children, offset)

    @staticmethod
    def save2File(writer: PdfFileWriter, newFileName: str):
        with open(newFileName, 'wb') as fout:
            writer.write(fout)

    @staticmethod
    def getBookmarksByPage(bookmarks: List[Tree], pageStart: int, pageEnd: int, repage = True):
        # repage代表是否按照起始页重新设定书签的页码，在分割的时候是需要的
        nbm: List[Tree] = []
        for bm in bookmarks:
            npage = bm.page
            if repage:
                # 因为pdf页码是从1开始的
                npage = bm.page - pageStart + 1

            if bm.page >= pageStart and bm.page <= pageEnd:
                nbm.append(Tree(bm.title, npage, []))

            for bm2 in bm.children:
                parent1 = nbm[-1]
                npage = bm2.page
                if repage:
                    npage = bm2.page - pageStart + 1

                if bm2.page >= pageStart and bm2.page <= pageEnd:
                    parent1.children.append(Tree(bm2.title, npage, []))

                for bm3 in bm2.children:

                    parent1 = nbm[-1]
                    parent2 = parent1.children[-1]
                    npage = bm3.page
                    if repage:
                        npage = bm3.page - pageStart + 1

                    if bm3.page >= pageStart and bm3.page <= pageEnd:
                        parent2.children.append(Tree(bm3.title, npage, []))

                    for bm4 in bm3.children:
                        parent1 = nbm[-1]
                        parent2 = parent1.children[-1]
                        parent3 = parent2.children[-1]
                        npage = bm4.page
                        if repage:
                            npage = bm4.page - pageStart + 1

                        if bm4.page >= pageStart and bm4.page <= pageEnd:
                            parent3.children.append(Tree(bm4.title, npage, []))

        return nbm

    @staticmethod
    def getAllBookmarks(pdf: PdfFileReader):
        bookmarks: List[Tree] = []
        bookmarkList = pdf.getOutlines()
        for item in bookmarkList:
            if isinstance(item, list):
                PDFHandler.outlines2Tree(pdf, item, bookmarks[-1])
                continue

            bookmarks.append(PDFHandler.outline2Tree(pdf, item))

        return bookmarks

    @staticmethod
    def outlines2Tree(pdf: PdfFileReader, item, node: Tree):
        for subItem in item:
            # 如果是list说明是上一个元素的子元素
            if isinstance(subItem, list):
                PDFHandler.outlines2Tree(pdf, subItem, node.children[-1])
            else:
                node.children.append(PDFHandler.outline2Tree(pdf, subItem))

    @staticmethod
    def addBookmarks(writer: PdfFileWriter, bookmarks: List[Tree]):
        count = 0
        for b in bookmarks:
            count += 1
            # 1级书签
            node = PDFHandler.addBookmark(writer, b.title, b.page, None)
            if len(b.children) == 0:
                continue

            # 2级书签
            for b2 in b.children:
                count += 1
                node2 = PDFHandler.addBookmark(writer, b2.title, b2.page, node)

                if len(b2.children) == 0:
                    continue

                # 3级书签
                for b3 in b2.children:
                    count += 1
                    node3 = PDFHandler.addBookmark(writer, b3.title, b3.page, node2)

                    if len(b3.children) == 0:
                        continue
                    
                    # 4级书签
                    for b4 in b3.children:
                        count += 1
                        PDFHandler.addBookmark(writer, b4.title, b4.page, node3)
        return count

    @staticmethod
    def addBookmark(
        write: PdfFileWriter, 
        title: str, 
        page: int, 
        parent = None, 
        color = None, 
        fit = '/Fit',
        ):
        return write.addBookmark(title, page - 1, parent = parent, color = color, fit = fit)

    @staticmethod
    def outline2Tree(pdf: PdfFileReader, item):
        page = pdf.getDestinationPageNumber(item)+1
        title = item.title
        return Tree(title, page, [])
