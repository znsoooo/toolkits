# TODO
# RICH2的字体
# 字数统计bug
# 测试其他win平台是否可以读取保存office

# v1.06
# 20200614
# 提取文档图片和追加拖入文档选项
# 去除置顶选项
# 检测并允许多文件文本依次保存为多个文件
# 多文件模式按文件名排序
# 多文件展示效果调整(分割线/非完整文件名/文件行数)
# 提出MyWalk流程函数

import os
import wx

import compare
import compress
import file2text

__ver__ = 'v1.06'


def SplitFiles(s):
    lines = s.split('\n')
    titles = []
    ress = []
    status = -1
    for line in lines:
        status += 1
        if status == 0: # split line1
            continue
        elif status == 1 and line.startswith('file: '):
            titles.append(line[6:])
            res = ''
        elif status == 2 and line.startswith('lines: '):
            res_cnt = int(line[7:])
        elif status == 3: # split line2
            continue
        elif 3 < status < 4 + res_cnt:
            res += line + '\n'
        elif status == 4 + res_cnt: # split line1
            status = 0
            ress.append(res[:-1]) # 去掉最后一个'\n'
    return titles, ress


def MyWalk(paths):
    for path in sorted(paths): # 否则鼠标拖拽时点击位置不同造成顺序不同:
        if os.path.isfile(path):
            yield path
        else:
            for path2, folders, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(path2, file)
                    yield full_path


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
        self.filenames = []

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
        save_media   = self.parent.parent.cb1.GetValue()
        multi_choice = self.parent.parent.cb2.GetValue()
        if not multi_choice:
            self.filenames = filenames
        else:
            self.filenames += filenames
        filenames = self.filenames

        if len(filenames) == 1 and os.path.isfile(filenames[0]):
            filename = filenames[0]
            ret, ss = file2text.file2text(filename, save_media=save_media)
            if ret:
                dlg = wx.MessageDialog(None, ret, 'Open Error: %s'%filename)
                dlg.ShowModal()

            self.text.SetValue(ss)
            self.path = os.path.dirname(filename)
            self.file = os.path.basename(filename)
            self.title = os.path.splitext(os.path.basename(filename))[0]

        else:
            line1 = '='*20
            line2 = '~'*20
            res = []
            error = []
            for filename in MyWalk(filenames):
                ret, ss = file2text.file2text(filename, save_media=save_media)
                if ret:
                    error.append(filename)
                res.append(('%s\nfile: %s\nlines: %s\n%s\n%s\n')%(line1, os.path.split(filename)[1], ss.count('\n')+1, line2, ss))

            if len(error):
                dlg = wx.MessageDialog(None, '\n'.join(error), 'Open Error: %s Files'%len(error))
                dlg.ShowModal()

            self.text.SetValue(''.join(res) + line1)
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

        parent.ToggleWindowStyle(wx.STAY_ON_TOP) # 窗口置顶方便拖拽文件

        sampleList = ['原文', '对比', '差异', '压缩']
        st1 = wx.StaticText(self, -1, '')
        st2 = wx.StaticText(self, -1, '')
        st3 = wx.StaticText(self, -1, '产生结果：')
        ch1 = wx.Choice(self, -1, choices=sampleList)
        self.cb1 = wx.CheckBox(self, -1, '提取')
        self.cb2 = wx.CheckBox(self, -1, '追加')
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
        box.Add(self.cb1, 0, wx.EXPAND|wx.LEFT, 8)
        box.Add(self.cb2, 0, wx.EXPAND)
        box.Add(bt1, 0)
        box.Add(bt2, 0)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND|wx.ALL)
        sizer.Add(box, 0, wx.EXPAND)
        self.SetSizer(sizer)

        ch1.Bind(wx.EVT_CHOICE, self.OnChoice)
        bt1.Bind(wx.EVT_BUTTON, self.OnOpen)
        bt2.Bind(wx.EVT_BUTTON, self.OnSave)

        accelTbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('O'), bt1.GetId()),
                                        (wx.ACCEL_CTRL, ord('S'), bt2.GetId())])
        self.SetAcceleratorTable(accelTbl)

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
        titles, ress = [title], [res]
        if res.startswith('='*20) and res.endswith('='*20):
            dlg = wx.MessageDialog(None, '检测到多个文件，是否依次保存为单独的文件？', '提示', wx.YES_NO)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                titles, ress = SplitFiles(res)

        for title, res in zip(titles, ress):
            dlg = wx.FileDialog(self,
                                defaultDir = path,
                                defaultFile = os.path.splitext(title)[0],
                                wildcard = '文本文件 (*.txt)|*.txt|All files (*.*)|*.*',
                                style = wx.FD_SAVE
                                      | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                with open(path, 'w', encoding='u8') as f:
                    f.write(res)


if __name__ == '__main__':
    app = wx.App()
    frm = wx.Frame(None, size=(600,400))
    win = MyPanel(frm)
    frm.Centre()
    frm.Show()
    app.MainLoop()
