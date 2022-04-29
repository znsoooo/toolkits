import wx

import ui
import eversheet

__ver__ = 'v0.3.0'



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
        values = self.GetValues()
        ret = eversheet.history(*values[:2])
        wx.MessageBox(ret)

    def OnSubmit(self, evt):
        values = self.GetValues()
        ret = eversheet.submit(*values)
        wx.MessageBox(ret)

    def OnClose(self, evt):
        username, password, *_ = self.GetValues()
        data = [self.mac, username, password]
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
    frm = MyDialog('保密云表自查 %s' % __ver__, (240, 260))
    app.MainLoop()
