# TODO
# RICH2的字体
# Ctrl追加拖入
# 字数统计bug
# 测试其他win平台是否可以读取保存office

import os
import wx

import compare
import compress
import file2text

__ver__ = 'v1.05'

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

        self.parent = parent
        self.text = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE|wx.TE_RICH2)
######        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'MingLiU')
######        self.text.SetFont(font)
######        self.text.SetStyle(0, 9, wx.TextAttr(wx.NullColour, wx.NullColour, font))
        self.path = ''
        self.file = self.title = '未命名'

        dt = MyFileDropTarget(self)
        self.text.SetDropTarget(dt)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(sizer)

        self.text.Bind(wx.EVT_TEXT, self.EvtText)

    def EvtText(self, evt):
        length = len(evt.GetString())
        if length:
            self.parent.parent.info.SetLabel(' 字数: %s'%length)
        else:
            self.parent.parent.info.SetLabel(' 联系作者: QQ11313213')

    def SetFiles(self, filenames):
        if len(filenames) == 1 and os.path.isfile(filenames[0]):
            filename = filenames[0]
            ret, ss = file2text.file2text(filename)
            if ret:
                dlg = wx.MessageDialog(None, ret, 'Open Error: %s'%filename)
                dlg.ShowModal()

            self.text.SetValue(ss)
            self.path = os.path.dirname(filename)
            self.file = os.path.basename(filename)
            self.title = os.path.splitext(os.path.basename(filename))[0]

        else:
            res = []
            error = []
            for filename in filenames:
                if os.path.isdir(filename):
                    for path, folders, files in os.walk(filename):
                        for file in files:
                            filename2 = os.path.join(path, file)
                            ret, ss = file2text.file2text(filename2)
                            if ret:
                                error.append(filename2)
                            res.append(('='*80+'\n\nfile: %s\n\n'+'='*80+'\n\n%s\n\n')%(filename2, ss))
                else:
                    ret, ss = file2text.file2text(filename)
                    if ret:
                        error.append(filename)
                    res.append(('='*80+'\n\nfile: %s\n\n'+'='*80+'\n\n%s\n\n')%(filename, ss))
            if len(error):
                dlg = wx.MessageDialog(None, '\n'.join(error), 'Open Error: %s Files'%len(error))
                dlg.ShowModal()

            self.text.SetValue(''.join(res))
            self.path = os.path.dirname(filenames[0])
            self.file = '%s个文档'%len(res)
            self.title = self.file

        os.chdir(self.path)
        self.parent.file = self.title + '.txt'
        frm.SetTitle('%s - 文本比对 %s'%(self.file, __ver__))


class Notebook(wx.Notebook):
    def __init__(self, parent, sampleList):
        wx.Notebook.__init__(self, parent)

        self.parent = parent

        self.select = 2
        self.text = [''] * 3

        p1 = NewPage(self)
        p2 = NewPage(self)
        p3 = NewPage(self)
        p1.text.SetFocus()

        self.AddPage(p1, sampleList[0])
        self.AddPage(p2, sampleList[1])
        self.AddPage(p3, sampleList[2])

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        self.OnPageChanged(-1)

    def OnPageChanged(self, event):
        for i in range(3):
            self.text[i] = self.GetPage(i).text.GetValue()
        page = self.GetCurrentPage()
        self.title = page.file
        self.file = page.title + '.txt'

        if self.select == self.GetSelection() or (self.select == 3 and self.GetSelection() == 2):
            if self.select == 0:
                res = compare.removeDiff(self.text[1], self.text[2], reverse=True)
                self.title = '原文 %s 移除 %s 的差异'%(self.GetPage(1).title, self.GetPage(2).title)
            elif self.select == 1:
                try:
                    res = compress.decompress(self.text[0], self.text[2])
                except:
                    res = compare.removeDiff(self.text[0], self.text[2])
                self.title = '原文 %s 增加 %s 的差异'%(self.GetPage(0).title, self.GetPage(2).title)
            elif self.select == 2:
                res = compare.makeDiff(self.text[0], self.text[1])
                self.title = '比较 %s 和 %s 的结果'%(self.GetPage(0).title, self.GetPage(1).title)
            elif self.select == 3:
                res = compress.compress(self.text[0], self.text[1])
                self.title = '比较 %s 和 %s 的结果(压缩)'%(self.GetPage(0).title, self.GetPage(1).title)
            self.GetCurrentPage().text.SetValue(res)
            self.file = self.title + '.txt'

        length = len(self.GetCurrentPage().text.GetValue())
        if length:
            self.parent.info.SetLabel(' 字数: %s'%length)
        else:
            self.parent.info.SetLabel(' 联系作者: QQ11313213')
        frm.SetTitle('%s - 文本比对 %s'%(self.title, __ver__))


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sampleList = ['原文', '对比', '差异', '压缩']
        st1 = wx.StaticText(self, -1, '')
        st2 = wx.StaticText(self, -1, '')
        st3 = wx.StaticText(self, -1, '产生结果：')
        ch1 = wx.Choice(self, -1, choices=sampleList)
        cb1 = wx.CheckBox(self, -1, '最前', style=wx.NO_BORDER)
        bt1 = wx.Button(self, label='打开')
        bt2 = wx.Button(self, label='保存')

        ch1.SetSelection(2)

        self.info = st1
        self.notebook = Notebook(self, sampleList)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(st1, 1, wx.ALIGN_CENTER_VERTICAL)
        box.Add(st2, 0, wx.ALIGN_CENTER_VERTICAL)
        box.Add(st3, 0, wx.ALIGN_CENTER_VERTICAL)
        box.Add(ch1, 0)
        box.Add(cb1, 0, wx.EXPAND|wx.LEFT, 5)
        box.Add(bt1, 0)
        box.Add(bt2, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL)
        sizer.Add(box, 0, wx.EXPAND)
        self.SetSizer(sizer)

        cb1.Bind(wx.EVT_CHECKBOX, self.OnCheckbox)
        ch1.Bind(wx.EVT_CHOICE, self.OnChoice)
        bt1.Bind(wx.EVT_BUTTON, self.OnOpen)
        bt2.Bind(wx.EVT_BUTTON, self.OnSave)

        accelTbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('O'), bt1.GetId()),
                                        (wx.ACCEL_CTRL, ord('S'), bt2.GetId())])
        self.SetAcceleratorTable(accelTbl)

    def OnCheckbox(self, evt):
        frm.ToggleWindowStyle(wx.STAY_ON_TOP+1-evt.GetSelection())

    def OnChoice(self, evt):
        self.notebook.select = evt.GetSelection()
        self.notebook.OnPageChanged(-1)

    def OnOpen(self, evt):
        page = self.notebook.GetCurrentPage()
        path = page.path
        dlg = wx.FileDialog(self,
                            defaultDir = path,
                            style = wx.FD_OPEN
                                  | wx.FD_MULTIPLE
                                  | wx.FD_CHANGE_DIR
                                  | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            page.SetFiles(dlg.GetPaths())

    def OnSave(self, evt):
        page = self.notebook.GetCurrentPage()
        res = page.text.GetValue()
        path = page.path
        title = self.notebook.file
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
    frm = wx.Frame(None, size=(600,400))
    win = MyPanel(frm)
    frm.Centre()
    frm.Show()
    app.MainLoop()
