# Useage:
# 读取: 在文件选取对话框中多选多个文件，批量导入待修改文件名列表
# 标密: 文件名自动密级标注、手动模式、文件名重复自动追加编号、高密级标注警告
# 去标: 去除文件名中的密级标注，如果密级标记前后存在括号将一并去除
# 确认: 批量修改文件名并返回程序运行结果
# 撤回: 返回一步操作

# 日志: 本地产生log文件，误操作后可以回滚（配合使用手动模式）


# 20200507 build
# Ver 1.01
# 自定义增加密级
# 跳过已存在密级标注的文件
# 文件名重复自动增加编号
# 汇总运行情况说明
# 高密级标注警告
# 允许撤回
# 允许手动设置

# Ver 1.02
# 20200609
# 重构代码
# 更改页面布局
# 使用Frame实现box的效果
# 允许移除文件名中的密级
# 强制出log
# 支持手动批量添加文件

# Ver 1.03
# 20210324
# 改为正则表达式替换文件名
# 横向/纵向联合滚动进度条
# 行内不换行
# 随输入实时显示替换结果
# 增加"清除"按键
# 增加"交换"按键
# 去除"标密/去标/撤回"按键，改为使用正则表达式替换实现，去除手动标密功能


# TODO
# 遍历文件夹(仅前1000个文件)
# '非密'和'非秘'
# 行号


import os
import re
import time

import tkinter
import tkinter.filedialog
import tkinter.messagebox

# nopath:<ext:doc;ppt;xls;pps;docx;pptx;xlsx;pdf !公开 !非密 !内部 !秘密 !机密 !startwith:~>
# nopath:<ext:doc;ppt;xls;pps;docx;pptx;xlsx;pdf 秘密|机密 !★ !startwith:~> dm:>202007

# [\(（]秘密[\)）] (秘密★10年)
# [\(（]机密[\)）] (机密★20年)
# [\(（]([非秘机绝]密)?(内部)?(公开)?[\)）]
# $ (内部)
# ^ 内部★

# disks = ['E:/','D:/','C:/']
# exts  = ['.doc','.docx','.xls','.xlsx','.ppt','.pptx','.pps']
# ranks = ['公开','非密','内部','秘密','机密','绝密']


def UniqueFile(file): # Good!
    root, ext = os.path.splitext(file)
    cnt = 1
    while os.path.exists(file):
        file = '%s_%d%s'%(root, cnt, ext)
        cnt += 1
    return file


def RenameFiles(paths1, paths2):
    os.makedirs('log', exist_ok=1)
    f = open(time.strftime('log/rollback_%Y%m%d_%H%M%S.bat'), 'a') # cmd需要使用gbk编码

    cnt1 = cnt2 = 0
    for path1, path2 in zip(paths1, paths2):
        try:
            if path1 != path2 and os.path.exists(path1): # 左右一致跳过
                path22 = UniqueFile(path2)
                os.rename(path1, path22)
                f.write('move "%s" "%s"\n'%(path22, path1))
                cnt1 += 1
        except Exception as e:
            cnt2 += 1
            print(e)
    f.write('pause\n')
    f.close()
    tkinter.messagebox.showinfo('提示', '文件名批量标密已完成，列表共有%s个文件，完成%s个文件，失败%s个文件，未进行%s个文件。'%(len(paths1), cnt1, cnt2, (len(paths1)-cnt1-cnt2)))
    '''其他为重命名列表数目不一致或文件不存在。'''
    if cnt2:
        tkinter.messagebox.showinfo('重命名失败', '部分文件重命名失败，可能存在路径不合法、或者需要管理员权限，请用管理员方式运行本程序重试。')



class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.title('自动标密v1.03b （联系作者：QQ11313213）')

        box = tkinter.Frame(self)
        box1 = tkinter.Frame(box)
        box2 = tkinter.Frame(box)

        sc_h1 = tkinter.Scrollbar(box1, orient='horizontal')
        sc_h2 = tkinter.Scrollbar(box2, orient='horizontal')
        sc_v = tkinter.Scrollbar(box)

        self.tex1 = tkinter.Text(box1, width=0, height=0, wrap='none', xscrollcommand=sc_h1.set, yscrollcommand=sc_v.set) # width=height=0保证窗口拉伸时比例始终为1
        self.tex2 = tkinter.Text(box2, width=0, height=0, wrap='none', xscrollcommand=sc_h2.set)
        self.ent1 = tkinter.Entry(box1, width=0)
        self.ent2 = tkinter.Entry(box2, width=0)

        tkinter.Label(box1, text='原始路径：').pack(anchor='w')
        tkinter.Label(box2, text='修改路径：').pack(anchor='w')
        self.tex1.pack(fill='both', expand=True)
        self.tex2.pack(fill='both', expand=True)
        sc_h1.pack(fill='x')
        sc_h2.pack(fill='x')
        tkinter.Label(box1, text='正则匹配（不修改路径和后缀）：').pack(anchor='w')
        tkinter.Label(box2, text='正则替换（不修改路径和后缀）：').pack(anchor='w')
        self.ent1.pack(fill='both')
        self.ent2.pack(fill='both')

        self.tex1.config(yscrollcommand=lambda y1, y2: (sc_v.set(y1, y2), self.tex2.yview('moveto', y1)))
        self.tex2.config(yscrollcommand=lambda y1, y2: (sc_v.set(y1, y2), self.tex1.yview('moveto', y1)))
        sc_h1.config(command=lambda *k: (self.tex1.xview(*k), self.tex2.xview(*k)))
        sc_h2.config(command=lambda *k: (self.tex1.xview(*k), self.tex2.xview(*k)))
        sc_v .config(command=lambda *k: (self.tex1.yview(*k), self.tex2.yview(*k)))

        btn1 = tkinter.Button(self, text='确认', command=self.rename)
        btn2 = tkinter.Button(self, text='清除', command=self.clear)
        btn3 = tkinter.Button(self, text='读取', command=self.load)
        btn4 = tkinter.Button(self, text='交换', command=self.exchange)

        box.pack(side='top', fill='both', expand=True)
        box1.pack(side='left', fill='both', expand=True)
        sc_v.pack(side='left', fill='y')
        box2.pack(side='left', fill='both', expand=True)
        btn4.pack(side='right')
        btn3.pack(side='right')
        btn2.pack(side='right')
        btn1.pack(side='right')

        self.tex1.config(bg='#FFFFFF') # 有时系统设置会覆盖默认的白色(比如护眼绿色)
        self.tex2.config(state='disabled', bg='#F0F0F0') # 禁止编辑

        self.tex1.focus()
        self.ent1.insert(0, '$')
        self.ent2.insert(0, '(内部)')

        self.Center()

        self.bind('<KeyRelease>', self.refresh)


    def Center(self):
        self.withdraw() # 先withdraw隐藏再deiconify避免页面闪烁
        self.geometry('920x400')
        x = (self.winfo_screenwidth()  - 920) / 2  # 此处设置与窗口大小一致
        y = (self.winfo_screenheight() - 400) / 2
        self.geometry('+%d+%d'%(x, y))
        self.deiconify()


    def GetTexts(self):
        s1 = self.tex1.get('1.0', 'end')[:-1]
        s2 = self.tex2.get('1.0', 'end')[:-1]
        return s1, s2


    def GetRegulars(self):
        r1 = self.ent1.get()
        r2 = self.ent2.get()
        return r1, r2


    def SetTexts(self, s1=None, s2=None):
        if s1 is not None:
            self.tex1.delete('1.0', 'end')
            self.tex1.insert('1.0', s1)

        if s2 is not None:
            self.tex2.config(state='normal')
            self.tex2.delete('1.0', 'end')
            self.tex2.insert('1.0', s2)
            self.tex2.config(state='disabled')


    def refresh(self, evt=0):
        s1 = self.GetTexts()[0]
        r1, r2 = self.GetRegulars()
        try:
            paths2 = [os.path.join(os.path.dirname(p), re.sub(r1, r2, os.path.splitext(os.path.basename(p))[0]) + os.path.splitext(os.path.basename(p))[1]) for p in s1.split('\n')]
        except:
            paths2 = []
        self.SetTexts(s2='\n'.join(paths2))


    def load(self):
        files = tkinter.filedialog.askopenfilenames()
        if files:
            if self.tex1.get('1.0', 'end') != '\n': # Text为空时不在前面增加\n
                self.tex1.insert('end', '\n')
            self.tex1.insert('end', '\n'.join(files))

        self.refresh()


    def clear(self):
        self.SetTexts(s1='', s2='')


    def rename(self):
        s1, s2 = self.GetTexts()
        RenameFiles(s1.split('\n'), s2.split('\n'))


    def exchange(self):
        s1, s2 = self.GetTexts()
        self.SetTexts(s2, s1)



top = myPanel()
top.mainloop()

