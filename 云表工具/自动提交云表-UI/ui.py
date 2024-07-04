import wx


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        w1 = wx.TextCtrl(self)
        w2 = wx.TextCtrl(self)
        w3 = wx.SpinCtrl(self, min=2000, max=2099)
        w4 = wx.SpinCtrl(self, min=1, max=12)
        w5 = wx.SpinCtrl(self, value='1', min=0, max=99)
        w6 = wx.SpinCtrlDouble(self, value='1', min=0, max=99)

        self.widgets = [w1, w2, w3, w4, w5, w6]
        self.names   = ['用户名', '密码', '自查年', '自查月', '保密次数', '保密学时']

        gbs = wx.GridBagSizer(5, 5)

        for r, (n, w) in enumerate(zip(self.names, self.widgets)):
            gbs.Add(wx.StaticText(self, -1, n + ':'), (r, 0), flag=wx.ALIGN_CENTER_VERTICAL)
            gbs.Add(w, (r, 1), flag=wx.EXPAND)

        gbs.AddGrowableCol(1)

        bt1 = wx.Button(self, 101, '获取')
        bt2 = wx.Button(self, 102, '提交')
        bt2.SetFocus()

        box2 = wx.BoxSizer()
        box2.Add(bt1, 1)
        box2.Add(bt2, 1, wx.LEFT, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(gbs, 0, wx.ALL|wx.EXPAND, 5)
        box.Add((0, 0), 1)
        box.Add(box2, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(box)

        self.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox('Unfilled'))

        # for test
        # self.SetValues(['hello', None, 2022, 3, 4, 5])
        # print(self.GetValues())

    def GetValues(self):
        return [w.GetValue() for w in self.widgets]

    def SetValues(self, values):
        [w.SetValue(value) for w, value in zip(self.widgets, values) if value]


class MyFrame(wx.Frame):
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, -1, title, size=size)
        panel = MyPanel(self)
        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame('保密云表自查', (240, 270))
    app.MainLoop()
