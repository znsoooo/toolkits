# 20200922 build

# TODO
# 拖拽文件夹
# 支持单项增删
# 支持追加文件
# 提取时间信息
# 批量改名/增加后缀
# 格式筛选

import os
import csv

import wx
import wx.dataview as dv


__ver__ = 'v2'

FILE_MAILS = 'mails.csv'


def OpenCsv(file):
    with open(file) as f:
        return [row for row in csv.reader(f) if len(row) == 2] # 格式审查每行2列


def WriteCsv(data, file):
    with open(file, 'w', newline='', errors='ignore') as f: # TODO Error的处理方式?
        writer = csv.writer(f)
        writer.writerows(data)


def AnalyseFiles(namelist, filelist):
    data = []
    absence = []
    for name, mail in namelist:
        row = [name, mail, '']
        for file in filelist:
            basename = os.path.basename(file)
            if name in basename:
                row[2] = basename
                break
        data.append(row)
    return data


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        parent.SetTitle('文档统计助手 %s'%__ver__)

        self.data = []
        self.absence = []
        self.namelist = []
        self.filelist = []

        self.dvlc = dvlc = dv.DataViewListCtrl(self, style=dv.DV_ROW_LINES|dv.DV_MULTIPLE)
        for title, width in [['序号', 40], ['姓名', 80], ['邮箱', 150], ['文档', 300]]:
            dvlc.AppendTextColumn(title, width=width, align=wx.ALIGN_CENTER, flags=dv.DATAVIEW_COL_SORTABLE)

        lab0 = wx.StaticText(self, -1, '')
        self.lab1 = wx.StaticText(self, -1, '联系作者: QQ11313213')
        btn1 = wx.Button(self, -1, '导入模板')
        btn2 = wx.Button(self, -1, '打开文档')
        btn3 = wx.Button(self, -1, '复制邮箱')

        box = wx.BoxSizer(wx.VERTICAL)
        toolbar = wx.BoxSizer()
        toolbar.Add(self.lab1, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 8)
        toolbar.Add(btn1)
        toolbar.Add(btn2)
        toolbar.Add(btn3)
        box.Add(self.dvlc, 1, wx.EXPAND)
        box.Add(toolbar, 0, wx.EXPAND)

        self.SetSizer(box)

        btn1.Bind(wx.EVT_BUTTON, self.OnOpenFile)
        btn2.Bind(wx.EVT_BUTTON, self.OnOpenFiles)
        btn3.Bind(wx.EVT_BUTTON, self.OnCopy)


        if os.path.exists(FILE_MAILS):
            self.namelist = OpenCsv(FILE_MAILS)
            self.Refresh()


    def Refresh(self):
        self.data = AnalyseFiles(self.namelist, self.filelist)

        self.dvlc.DeleteAllItems()
        for i, row in enumerate(self.data):
            self.dvlc.AppendItem([i+1] + row)

        self.absence = ['%s<%s>,'%(name, mail) for name, mail, file in self.data if not file]
        text = '联系作者: QQ11313213'
        if len(self.namelist) - len(self.absence):
            text = '文档: %s, 名单: %s, 匹配: %s, 空缺: %s'%(len(self.filelist), len(self.namelist), len(self.namelist)-len(self.absence), len(self.absence))
        self.lab1.SetLabel(text)


    def OnCopy(self, evt):
        if not len(self.absence):
            dlg = wx.MessageBox('共有0人空缺文档，无需复制邮箱地址。', '确认')
            return

        text = ''.join(self.absence)
        dlg = wx.MessageBox('共有%d人空缺文档，复制邮箱地址：\n%s\n%s'%(len(self.absence), '—'*14, text), '确认', wx.YES_NO)
        if dlg == 2:
            wx.TheClipboard.SetData(wx.TextDataObject(text))


    def OnOpenFile(self, evt):
        dlg = wx.FileDialog(self, style=wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPaths()[0]
            self.namelist = OpenCsv(path)
            WriteCsv(self.namelist, FILE_MAILS)
            self.Refresh()


    def OnOpenFiles(self, evt):
        dlg = wx.FileDialog(self, style=wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.filelist = dlg.GetPaths()
            self.Refresh()


if __name__ == '__main__':
    app = wx.App()
    frm = wx.Frame(None, size=(620, 600))
    win = MyPanel(frm)
    frm.Centre()
    frm.Show()
    app.MainLoop()
