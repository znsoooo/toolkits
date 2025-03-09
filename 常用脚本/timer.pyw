import wx
import time
import lsx

class TimerDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="计时器", size=(300, 200))
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())

        self.panel = wx.Panel(self)
        self.display = wx.StaticText(self.panel, label="0.00", style=wx.ALIGN_CENTER)
        self.display.SetFont(wx.Font(40, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.sizer = sizer = wx.BoxSizer()
        sizer.Add(self.display, 1, wx.ALIGN_CENTER)
        self.panel.SetSizer(sizer)

        self.Center()
        self.Show()
        self.timer.Start(50)

    def OnTimer(self, event):
        self.display.SetLabel(f"{lsx.clock():.2f}")
        self.sizer.Layout()

if __name__ == "__main__":
    app = wx.App()
    dlg = TimerDialog()
    app.MainLoop()
