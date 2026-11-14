import wx


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='题库搜索', size=(700, 600))
        self.questions = []
        self.Load()
        self.BuildUi()
        self.Centre()
        self.OnSearch(None)
        self.Show()

    def Load(self):
        try:
            with open('questions.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            self.questions = [q.strip() for q in content.split('\n\n') if q.strip()]
        except FileNotFoundError:
            self.questions = []
            wx.MessageBox('未找到 questions.txt 文件', '提示', wx.OK | wx.ICON_WARNING)

    def BuildUi(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.input.SetHint('输入关键词，空格隔开（不区分大小写）')
        self.input.Bind(wx.EVT_TEXT, self.OnSearch)
        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        self.input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        vbox.Add(self.input, 0, wx.EXPAND | wx.ALL, 5)

        self.result = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        vbox.Add(self.result, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        panel.SetSizer(vbox)

    def OnKeyDown(self, evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.input.Clear()
        else:
            evt.Skip()

    def OnSearch(self, evt):
        text = self.input.GetValue()
        self.result.SetValue('')
        if not text:
            self.result.SetValue('\n\n'.join(self.questions))
            return

        keywords = [kw.lower() for kw in text.split()]
        matched = [q for q in self.questions if all(kw in q.lower() for kw in keywords)]

        if not matched:
            self.result.SetValue('没有匹配的题目')
            return

        # 拼接结果并记录每段题目的起始偏移
        full_text = ''
        segments = []  # (start, end) 每个题目的范围
        for i, q in enumerate(matched):
            if i > 0:
                full_text += '\n\n'
            start = len(full_text)
            full_text += q
            segments.append((start, len(full_text)))

        self.result.SetValue(full_text)

        # 高亮：对每个题目范围内的每个关键词，找出所有出现位置
        attr = wx.TextAttr()
        # attr.SetTextColour(wx.Colour(255, 255, 255))
        attr.SetBackgroundColour(wx.Colour(127, 255, 127))  # 绿色背景

        for start, end in segments:
            segment_text = full_text[start:end]
            segment_lower = segment_text.lower()
            for kw in keywords:
                if not kw:
                    continue
                idx = segment_lower.find(kw)
                while idx != -1:
                    self.result.SetStyle(start + idx, start + idx + len(kw), attr)
                    idx = segment_lower.find(kw, idx + len(kw))


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
