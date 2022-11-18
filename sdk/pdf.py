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
    # 什么都不做
    NONE = 'none'

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

            bookmarks = self.getAllBookmarks()
            self.addBookmarks(bookmarks)
            
        elif mode == PDFHandleMode.NEWLY:
            for idx in range(self.pagesNum):
                page = self.__pdf.getPage(idx)
                self.__writeablePdf.insertPage(page, idx)

    def getBookmarksByPage(self, pageStart: int, pageEnd: int, repage = True):
        # repage代表是否按照起始页重新设定书签的页码，在分割的时候是需要的
        bookmarks = self.getAllBookmarks()
        nbm: list[Tree] = []
        for bm in bookmarks:
            if bm.page < pageStart or bm.page > pageEnd:
                continue
            
            npage = bm.page
            if repage:
                npage = bm.page - pageStart + 1

            nbm.append(Tree(bm.title, npage, []))

            for bm2 in bm.children:
                if bm2.page < pageStart or bm2.page > pageEnd:
                    continue

                parent1 = nbm[-1]
                npage = bm2.page
                if repage:
                    npage = bm2.page - pageStart + 1
                parent1.children.append(Tree(bm2.title, npage, []))

                for bm3 in bm2.children:
                    if bm3.page < pageStart or bm3.page > pageEnd:
                        continue

                    parent1 = nbm[-1]
                    parent2 = parent1.children[-1]
                    npage = bm3.page
                    if repage:
                        npage = bm3.page - pageStart + 1
                    parent2.children.append(Tree(bm3.title, npage, []))

                    for bm4 in bm3.children:
                        if bm4.page < pageStart or bm4.page > pageEnd:
                            continue
                        
                        parent1 = nbm[-1]
                        parent2 = parent1.children[-1]
                        parent3 = parent2.children[-1]
                        npage = bm4.page
                        if repage:
                            npage = bm4.page - pageStart + 1
                        parent3.children.append(Tree(bm4.title, npage, []))

        return nbm

    def split2File(self, start: int, end: int): 
        pdfWriter = writer()
        for idx in range(start, end + 1):
            page = self.__pdf.getPage(idx)
            pdfWriter.insertPage(page, idx-start)
        
        bookmarks = self.getBookmarksByPage(start, end)
        # 因为分割了，所以页码会发生变化
        self.__addBookmarks(pdfWriter, bookmarks)
        self.__save2File(pdfWriter, self.fileName + "_{0}-{1}.pdf".format(start, end))
        
    def getAllBookmarks(self):
        bookmarks: list[Tree] = []
        bookmarkList = self.__pdf.getOutlines()
        for item in bookmarkList:
            if isinstance(item, list):
                self.__parseSubOutlines(item, bookmarks[-1])
                continue

            bookmarks.append(self.__toTreeNode(item))

        return bookmarks

    def bookmarks2Txt(self, bookmarks):
        with open(self.fileName + ".txt", "w", encoding='utf-8') as f:
            for item in bookmarks:
                f.write(self.__treeNode2LineStr(item, 1))
                for item2 in item.children:
                    f.write(self.__treeNode2LineStr(item2, 2))
                    for item3 in item2.children:
                        f.write(self.__treeNode2LineStr(item3, 3))
                        for item4 in item3.children:
                            f.write(self.__treeNode2LineStr(item4, 4))

    def __treeNode2LineStr(self, item: Tree, level: int):
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
        
    def __parseSubOutlines(self, item, node: Tree):
        for subItem in item:
            # 如果是list说明是上一个元素的子元素
            if isinstance(subItem, list):
                self.__parseSubOutlines(subItem, node.children[-1])
            else:
                node.children.append(self.__toTreeNode(subItem))

    def __toTreeNode(self, item):
        page = self.__pdf.getDestinationPageNumber(item)+1
        title = item.title
        return Tree(title, page, [])

    def save2File(self, newFileName):
        # 保存修改后的PDF文件内容到文件中
        self.__save2File(self.__writeablePdf, newFileName)

    def __save2File(self, writer, newFileName):
        with open(newFileName, 'wb') as fout:
            writer.write(fout)

    def addBookmark(self, title: str,page,parent = None, color = None, fit = '/Fit'):
        return self.__addBookmark(self.__writeablePdf, title, page, parent, color, fit)

    def __addBookmark(self, write, title: str,page,parent = None, color = None, fit = '/Fit'):
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
        return write.addBookmark(title,page - 1,parent = parent,color = color,fit = fit)

    def addBookmarks(self, bookmarks):
        return self.__addBookmarks(self.__writeablePdf, bookmarks)

    def __addBookmarks(self, writer, bookmarks):
        count = 0
        for b in bookmarks:
            count += 1
            # 1级书签
            node = self.__addBookmark(writer, b.title, b.page, None)
            if len(b.children) == 0:
                continue

            # 2级书签
            for b2 in b.children:
                count += 1
                node2 = self.__addBookmark(writer, b2.title, b2.page, node)

                if len(b2.children) == 0:
                    continue

                # 3级书签
                for b3 in b2.children:
                    count += 1
                    node3 = self.__addBookmark(writer, b3.title, b3.page, node2)

                    if len(b3.children) == 0:
                        continue
                    
                    # 4级书签
                    for b4 in b3.children:
                        count += 1
                        self.__addBookmark(writer, b4.title, b4.page, node3)
        return count

    def readBookmarksFromTxt(self, txtFilePath):
        bookmarks: list[Tree] = []
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

    def addBookmarksByReadTxt(self, txtFilePath):
        bookmarks = self.readBookmarksFromTxt(txtFilePath)
        self.addBookmarks(bookmarks)