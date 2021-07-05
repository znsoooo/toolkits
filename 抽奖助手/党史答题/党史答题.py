# build 20210527

# TODO
# log信息

import wx
import csv
import random


WX_ETLR = wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT


def ReadCsv(file):
    with open(file) as f:
        return list(csv.reader(f))


class MyPanel(wx.Panel):
    def __init__(self, parent):
        parent.SetTitle('党史答题 v1.01')
        parent.SetSize((900, 600))
        parent.Center()
        wx.Panel.__init__(self, parent)

        ST = lambda s: wx.StaticText(self, -1, s)

        self.database = []
        self.pointer  = 0
        self.teams = [[0 for i in range(N)],
                      [wx.SpinCtrl(self, i, min=-10000, max=10000) for i in range(N)],
                      [wx.Choice(self) for i in range(N)]]

        self.question = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.answer   = wx.TextCtrl(self)
        self.choices  = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        groups        = wx.GridBagSizer(10, 10)
        toolbar       = wx.BoxSizer()

        for i in range(N):
            groups.Add(ST('%d队:'%(i+1)), (0, 2*i), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            groups.Add(ST('得分:'),       (1, 2*i), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
            groups.Add(self.teams[2][i], (0, 2*i+1), flag=wx.EXPAND)
            groups.Add(self.teams[1][i], (1, 2*i+1), flag=wx.EXPAND)
            groups.AddGrowableCol(2*i+1)

        self.right = wx.SpinCtrl(self, -1, '1')
        self.wrong = wx.SpinCtrl(self)
        impo   = wx.Button(self, -1, '导入')
        zero   = wx.Button(self, -1, '清空')
        prev   = wx.Button(self, -1, '上一题')
        next   = wx.Button(self, -1, '下一题')
        submit = wx.Button(self, -1, '确认提交')

        toolbar.Add(ST('答对得分:'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        toolbar.Add(self.right, 0, wx.RIGHT, 10)
        toolbar.Add(ST('答错扣分:'), 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        toolbar.Add(self.wrong, 0, wx.RIGHT, 10)
        toolbar.Add(ST(''), 1, wx.RIGHT, 10)
        toolbar.Add(impo,   0, wx.LEFT, 10)
        toolbar.Add(zero,   0, wx.LEFT, 10)
        toolbar.Add(prev,   0, wx.LEFT, 10)
        toolbar.Add(next,   0, wx.LEFT, 10)
        toolbar.Add(submit, 0, wx.LEFT, 10)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(ST('题目：'),   0, WX_ETLR, 10)
        box.Add(self.question, 2, WX_ETLR, 10)
        box.Add(ST('选项：'),   0, WX_ETLR, 10)
        box.Add(self.choices,  3, WX_ETLR, 10)
        box.Add(ST('答案：'),   0, WX_ETLR, 10)
        box.Add(self.answer,   0, wx.EXPAND|wx.ALL, 10)
        box.Add(groups,        0, wx.EXPAND|wx.ALL, 10)
        box.Add(toolbar,       0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(box)

        impo.Bind(wx.EVT_BUTTON, self.OnOpen)
        zero.Bind(wx.EVT_BUTTON, self.OnClear)
        prev.Bind(wx.EVT_BUTTON, self.OnPrev)
        next.Bind(wx.EVT_BUTTON, self.OnNext)
        submit.Bind(wx.EVT_BUTTON, self.OnSubmit)
        for sc in self.teams[1]:
            sc.Bind(wx.EVT_SPINCTRL, self.OnSpinCtrl)

        # self.OnOpen(-1)
        # wx.CallAfter(self.OnOpen, -1)
        self.ShowQuestion()


    def ShowQuestion(self):
        if self.database:
            q, a, *ss = self.database[self.pointer]
            self.question.SetValue('%d/%d: %s'%(self.pointer+1, len(self.database), q))
        else:
            q, a, *ss = ['', '']
            self.question.SetValue('')

        self.answer.SetValue('')
        self.choices.SetValue('\n\n'.join(ss))

        for choice in self.teams[2]:
            choice.SetItems(['------']+list('ABCDEFG'[:len(ss)]))
            choice.SetSelection(0)

        self.ShowScore()


    def ShowScore(self):
        for t, team in enumerate(self.teams[2]):
            self.teams[1][t].SetValue(self.teams[0][t])


    def OnSpinCtrl(self, evt):
        self.teams[0][evt.GetId()] = evt.GetInt()


    def OnOpen(self, evt):
        dlg = wx.FileDialog(self, wildcard='题库文件 (*.csv)|*.csv', style=wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                data = ReadCsv(path)
                random.shuffle(data)
                self.database.extend(data)
            self.ShowQuestion()


    def OnClear(self, evt):
        self.database.clear()
        self.pointer = 0
        self.ShowQuestion()

        
    def OnPrev(self, evt):
        if self.pointer > 0:
            self.pointer -= 1
            self.ShowQuestion()


    def OnNext(self, evt):
        if self.pointer < len(self.database) - 1:
            self.pointer += 1
            self.ShowQuestion()


    def OnSubmit(self, evt):
        if not self.database:
            return
        q, a, *ss = self.database[self.pointer]
        dlg = wx.MessageDialog(None, '正确答案：%s'%a, '答案')
        dlg.ShowModal()
        self.answer.SetValue(a)
        index = 'ABCDEFG'.index(a)
        for t, team in enumerate(self.teams[2]):
            if team.GetSelection(): # 非默认项
                if index == team.GetSelection() - 1:
                    self.teams[0][t] += self.right.GetValue()
                else:
                    self.teams[0][t] -= self.wrong.GetValue()
        self.ShowScore()



app = wx.App()

dlg = wx.TextEntryDialog(None, '输入数字：', '参赛队伍数量', '6')
if dlg.ShowModal() == wx.ID_OK:
    N = int(dlg.GetValue())
else:
    N = 6

frm = wx.Frame(None)
pnl = MyPanel(frm)
frm.Show()
app.MainLoop()


