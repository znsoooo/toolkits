import wx

import ui
import eversheet

__ver__ = 'v0.4.0'


class Bingo(wx.Dialog):
    def __init__(self, parent, bs):
        wx.Dialog.__init__(self)
        self.Create(parent, -1, 'Powered by lsx!')
        bmp = wx.Bitmap(wx.Image('donate.png'))
        img = wx.StaticBitmap(self, -1, bmp)
        self.Fit()
        self.Center()
        self.ShowModal()


class MyPanel(ui.MyPanel):
    def __init__(self, parent):
        ui.MyPanel.__init__(self, parent)
        self.parent = parent
        self.mac, *user = eversheet.GetUserData('user.txt')
        self.SetValues(user)
        self.Bind(wx.EVT_BUTTON, self.OnHistory, id=101)
        self.Bind(wx.EVT_BUTTON, self.OnSubmit,  id=102)
        parent.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnHistory(self, evt):
        ret = eversheet.history(*self.GetValues()[:2])
        wx.MessageBox(ret)

    def OnSubmit(self, evt):
        values = self.GetValues()
        if not values[0]:
            return Bingo(self, 1)
        ret = eversheet.submit(*values)
        if ret.startswith('提交失败'):
            if wx.YES == wx.MessageBox(ret, style=wx.YES_NO):
                self.OnDelete()
        else:
            wx.MessageBox(ret)

    def OnDelete(self):
        ret = eversheet.delete(*self.GetValues()[:4])
        wx.MessageBox(ret)
        self.OnSubmit(-1)

    def OnClose(self, evt):
        name, pswd, *_ = self.GetValues()
        data = [self.mac, name, pswd]
        eversheet.SaveUserData('user.txt', data)
        self.parent.Destroy()


class MyDialog(wx.Dialog):
    def __init__(self, title, size):
        wx.Dialog.__init__(self, None, -1, title, size=size)
        panel = MyPanel(self)
        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    locale = wx.Locale(wx.LANGUAGE_ENGLISH) # for read PNG
    frm = MyDialog('保密云表自查 %s' % __ver__, (240, 260))
    app.MainLoop()
