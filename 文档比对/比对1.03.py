# TODO
# 修改title
# 打开文件时errors='replace'

# v1.01
# 20190121
# 打开两个文件并输出对比结果
# 支持doc/docx/ppt/pptx/xls/xlsx/utf-8/gbk共8种格式

# v1.02
# 20190329
# 支持显示'参照/对比/差异'3个栏目的文本内容
# 可以'参照/对比/差异'中的两个项目输出第3个文本的内容

# v1.03
# 20190808

# 新增特性
# 支持文件拖拽载入
# 选项卡显示'原文/对比/差异'三个栏目的内容
# 通过下拉菜单确定'参照/对比/差异'中需要输出的项目
# 支持窗口置顶和取消
# 保存时的自动文件名和自动路径

# 流程优化
# GUI库从tkinter移植到wxPython
# file2text函数改为输入绝对路径
# 打开pptx文件时优化删除多余的属性名
# 文件打开错误时输出报错信息文本和弹窗
# 打开doc/ppt/xls时产生的临时文件优化不存在重复的后缀名
# compare库改为输入输出都是文本(原来是列表)
# 文件拖拽时修改工作路径(保存和打开时的自动路径有用)


import os
import re
import wx
import zipfile
from win32com import client

import compare

def file2text(path):
    root, ext = os.path.splitext(path)
    if path == '':
        ss = ''
    elif ext == '.doc':
        word = client.Dispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.SaveAs(root + '.temp.docx', 16)
        doc.Close()
        ss = file2text(root + '.temp.docx')
    elif ext == '.xls':
        excel = client.Dispatch('Excel.Application')
        xls = excel.WorkBooks.Open(path)
        xls.SaveAs(root + '.temp.xlsx', 51)
        xls.Close()
        ss = file2text(root + '.temp.xlsx')
    elif ext == '.ppt':
        powerpoint = client.Dispatch('PowerPoint.Application')
        powerpoint.Visible = 1
        ppt = powerpoint.Presentations.Open(path)
        ppt.SaveAs(root + '.temp.pptx')
        ppt.Close()
        ss = file2text(root + '.temp.pptx')
    elif ext == '.docx':
        f = zipfile.ZipFile(path, 'r')
        s = f.read('word/document.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<w:pPr>','\n'))
    elif ext == '.xlsx':
        f = zipfile.ZipFile(path, 'r')
        s = f.read('xl/sharedStrings.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<si>','\n'))
    elif ext == '.pptx':
        f = zipfile.ZipFile(path, 'r')
        files = f.namelist()
        s = ''
        max_page = 0
        for file in files:
            if file[:16] == 'ppt/slides/slide':
                max_page = max_page + 1
        for i in range(max_page):
            file = 'ppt/slides/slide%s.xml'%(i+1)
            s = s + file + f.read(file).decode() + '\n\n'
        s = s.replace('<a:p>','\n')
        s = re.sub(r'<p:attrName>.*?</p:attrName>','',s)
        ss = re.sub(r'<.*?>','',s)
    else:
        with open(path, 'rb') as f:
            ss = f.read()
        try:
            ss = ss.decode()
        except:
            try:
                ss = ss.decode('gbk') #, errors='replace')
            except Exception as e:
                ss = str(e)
                dlg = wx.MessageDialog(None, ss, 'Error')
                dlg.ShowModal()

    return ss


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        self.parent.SetFiles(filenames)
        return True


class NewPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self)
        self.Create(parent)

        self.text = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE)
        self.path = '.'
        self.title = '未命名'

        dt = MyFileDropTarget(self)
        self.text.SetDropTarget(dt)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)

    def SetFiles(self, filenames):
        filename = filenames[0]
        self.text.SetValue(file2text(filename))
        self.path = os.path.dirname(filename)
        self.title = os.path.splitext(os.path.basename(filename))[0]
        os.chdir(self.path)


class Notebook(wx.Notebook):
    def __init__(self, parent, sampleList):
        wx.Notebook.__init__(self, parent)

        self.select = 2
        self.text = [''] * 3

        p1 = NewPage(self)
        p2 = NewPage(self)
        p3 = NewPage(self)

        self.AddPage(p1, sampleList[0])
        self.AddPage(p2, sampleList[1])
        self.AddPage(p3, sampleList[2])

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def OnPageChanged(self, event=0, refresh=False):
        for i in range(3):
            self.text[i] = self.GetPage(i).text.GetValue()

        if refresh or self.select == event.GetSelection():
            if self.select == 0:
                res = compare.removeDiff(self.text[1], self.text[2], reverse=True)
            elif self.select == 1:
                res = compare.removeDiff(self.text[0], self.text[2])
            elif self.select == 2:
                res = compare.makeDiff(self.text[0], self.text[1])
            self.GetPage(self.select).text.SetValue(res)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sampleList = ['原文', '对比', '差异']
        st1 = wx.StaticText(self, -1, '产生结果：')
        ch1 = wx.Choice(self, -1, choices=sampleList)
        cb1 = wx.CheckBox(self, -1, '最前', style=wx.NO_BORDER)
        bt1 = wx.Button(self, label='打开')
        bt2 = wx.Button(self, label='保存')

        ch1.SetSelection(2)

        self.notebook = Notebook(self, sampleList)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(st1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL)
        box.Add(ch1, 1, wx.EXPAND|wx.ALL)
        box.Add(cb1, 1, wx.EXPAND|wx.LEFT, 20)
        box.Add(bt1, 1, wx.EXPAND|wx.ALL)
        box.Add(bt2, 1, wx.EXPAND|wx.ALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL)
        sizer.Add(box, 0, wx.ALIGN_RIGHT)
        self.SetSizer(sizer)

        cb1.Bind(wx.EVT_CHECKBOX, self.OnCheckbox)
        ch1.Bind(wx.EVT_CHOICE, self.OnChoice)
        bt1.Bind(wx.EVT_BUTTON, self.OnOpen)
        bt2.Bind(wx.EVT_BUTTON, self.OnSave)

    def OnCheckbox(self, evt):
        frm.ToggleWindowStyle(wx.STAY_ON_TOP+1-evt.GetSelection())

    def OnChoice(self, evt):
        self.notebook.select = evt.GetSelection()
        self.notebook.OnPageChanged(refresh=True)

    def OnOpen(self, evt):
        page = self.notebook.GetCurrentPage()
        path = page.path
        dlg = wx.FileDialog(self,
                            defaultDir = path,
                            style = wx.FD_OPEN
                                  | wx.FD_CHANGE_DIR
                                  | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            filename = paths[0]
            res = file2text(filename)
            page = self.notebook.GetCurrentPage()
            page.text.SetValue(res)
            page.path = os.path.dirname(filename)
            page.title = os.path.splitext(os.path.basename(filename))[0]
            self.notebook.OnPageChanged(refresh=True)

    def OnSave(self, evt):
        page = self.notebook.GetCurrentPage()
        res = page.text.GetValue()
        path = page.path
        title = page.title + '.txt'
        if self.notebook.GetSelection() == 2:
            title = '比较 %s 和 %s 的结果.txt'%(self.notebook.GetPage(0).title, self.notebook.GetPage(1).title)
        dlg = wx.FileDialog(self,
                            defaultDir = path,
                            defaultFile = title,
                            wildcard = '文本文件 (*.txt)|*.txt|All files (*.*)|*.*',
                            style = wx.FD_SAVE
                                  | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path, 'w') as f:
                f.write(res)


if __name__ == '__main__':
    app = wx.App()
    frm = wx.Frame(None, title='文本比对 v1.03', size=(600,400))
    win = MyPanel(frm)
    frm.Centre()
    frm.Show()
    app.MainLoop()


