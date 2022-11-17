# -*- coding: UTF-8 -*-
import os
from PyPDF2 import PdfFileReader as reader,PdfFileWriter as writer

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

class Tree:
    def __init__(self, title: str, page: str, children = []):
        self.title = title.lstrip()
        self.page = int(page)
        self.children = []

class PDFHandler(object):

    def __init__(self, filePath: str, mode = PDFHandleMode.COPY):
        # 只读的PDF对象
        self.__pdf = reader(filePath)
        # 获取PDF文件名（不带路径）
        self.fileName = os.path.basename(filePath)[0:-4]
        self.metadata = self.__pdf.getXmpMetadata()
        self.docInfo = self.__pdf.getDocumentInfo()
        self.pagesNum = self.__pdf.getNumPages()

        # 可写的PDF对象，根据不同的模式进行初始化
        self.__writeablePdf = writer()
        if mode == PDFHandleMode.COPY:
            for page in self.__pdf.pages:
                self.__writeablePdf.add_page(page)
            
            for outlines in self.__pdf.outlines:
                self.addOutlinesAsBookmark(self.__writeablePdf, outlines)
            
        elif mode == PDFHandleMode.NEWLY:
            for idx in range(self.pagesNum):
                page = self.__pdf.getPage(idx)
                self.__writeablePdf.insertPage(page, idx)

    def addOutlinesAsBookmark(self, writer, outlines):
        if not isinstance(outlines, list):
            page_nb = 0  # I don't know how to get the page number
            writer.add_bookmark(outlines.title, page_nb, None)
        else:
            for o in outlines:
                self.addOutlinesAsBookmark(writer, o)

    def save2file(self, newFileName):
        # 保存修改后的PDF文件内容到文件中
        with open(newFileName, 'wb') as fout:
            self.__writeablePdf.write(fout)

    def addBookmark(self,title: str,page,parent = None, color = None, fit = '/Fit'):
        '''
        往PDF文件中添加单条书签，并且保存为一个新的PDF文件
        :param str title: 书签标题
        :param int page: 书签跳转到的页码，表示的是PDF中的绝对页码，值为1表示第一页
        :paran parent: A reference to a parent bookmark to create nested bookmarks.
        :param tuple color: Color of the bookmark as a red, green, blue tuple from 0.0 to 1.0
        :param list bookmarks: 是一个'(书签标题，页码)'二元组列表，举例：[(u'tag1',1),(u'tag2',5)]，页码为1代表第一页
        :param str fit: 跳转到书签页后的缩放方式
        :return: None
        '''
        # 为了防止乱码，这里对title进行utf-8编码
        return self.__writeablePdf.addBookmark(title,page - 1,parent = parent,color = color,fit = fit)

    def addBookmarks(self, bookmarks):
        count = 0
        for b in bookmarks:
            count += 1
            # 1级书签
            node = self.addBookmark(b.title, b.page, None)
            if len(b.children) == 0:
                continue

            # 2级书签
            for b2 in b.children:
                count += 1
                node2 = self.addBookmark(b2.title, b2.page, node)

                if len(b2.children) == 0:
                    continue

                # 3级书签
                for b3 in b2.children:
                    count += 1
                    node3 = self.addBookmark(b3.title, b3.page, node2)

                    if len(b3.children) == 0:
                        continue
                    
                    # 4级书签
                    for b4 in b3.children:
                        count += 1
                        self.addBookmark(b4.title, b4.page, node3)
        return count

    def readBookmarksFromTxt(self, txtFilePath):
        bookmarks: list[Tree] = []
        with open(txtFilePath,'r') as fin:
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

    def addBookmarksByReadTxt(self, txtFilePath):
        bookmarks = self.readBookmarksFromTxt(txtFilePath)
        self.addBookmarks(bookmarks)