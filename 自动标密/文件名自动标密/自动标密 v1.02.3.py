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


# TODO
# 遍历文件夹(仅前1000个文件)
# '非密'和'非秘'
# 横向进度条
# 行号
# 联合滚动


import os
import re
import time

import tkinter
import tkinter.filedialog
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText


##disks = ['E:/','D:/','C:/']
##exts  = ['.doc','.docx','.xls','.xlsx','.ppt','.pptx','.pps']
ranks = ['公开','非密','内部','秘密','机密','绝密']


def Unique(head, tail):
    new_name = head + tail
    if not os.path.exists(new_name):
        return new_name
    else:
        cnt = 1
        while 1:
            cnt += 1
            new_name = '%s_%s%s'%(head, cnt, tail)
            if not os.path.exists(new_name):
                return new_name


def UnmarkFiles(paths1):
    paths2 = []
    for path in paths1:
        root, file = os.path.split(path)
        filename, ext = os.path.splitext(file)

        filename_new = filename
        for rank in ranks:
            filename_new = re.sub(r'[\(（]*%s[\)）]*'%rank, '', filename_new)

        if filename_new == filename:
            paths2.append(path)
        else:
            head = '%s\\%s'%(root, filename_new)
            paths2.append(Unique(head, ext))

    return paths2


def MarkFiles(paths1, rank='内部'):
    paths2 = []
    for path in paths1:
        root, file = os.path.split(path)
        filename, ext = os.path.splitext(file)

        marked = False
        for r in ranks:
            if r in filename:
                marked = True
                break

        if marked:
            paths2.append(path)
        else:
            head = '%s\\%s'%(root, filename)
            tail = '(%s)%s'%(rank, ext)
            paths2.append(Unique(head, tail))

    return paths2


def RenameFiles(paths1, paths2):
    log = ['pause']
    f = open('logging.csv.log', 'a')  # cmd需要使用gbk编码
    ttime = time.strftime('[%Y-%m-%d %H:%M:%S]\n', time.localtime())
    f.write(ttime)

    cnt1 = cnt2 = 0
    for path1, path2 in zip(paths1, paths2):
        try:
            if os.path.exists(path1) and not os.path.exists(path2):
                os.rename(path1, path2)
                f.write('move,"%s","%s"\n'%(path1, path2))
                cnt1 += 1
        except Exception as e:
            cnt2 += 1
            print(e)
    f.close()
    tkinter.messagebox.showinfo('提示', '文件名批量标密已完成，列表共有%s个文件，完成%s个文件，失败%s个文件，未进行%s个文件。'%(len(paths1), cnt1, cnt2, (len(paths1)-cnt1-cnt2)))
    '''其他为重命名列表数目不一致或文件不存在。'''
    if cnt2:
        tkinter.messagebox.showinfo('重命名失败', '部分文件重命名失败，可能存在路径不合法、或者需要管理员权限，请用管理员方式运行本程序重试。')


def setCenter(top):
    top.geometry('920x400')
    x = (top.winfo_screenwidth()  - 920) / 2  # 此处设置与窗口大小一致
    y = (top.winfo_screenheight() - 400) / 2
    top.geometry('+%d+%d'%(x, y))


class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')
        self.withdraw() # 先withdraw隐藏再deiconify显示可使setCenter不会导致页面闪烁

        self.title('自动标密v1.02 （联系作者：QQ11313213）')

        box = tkinter.Frame(self)
        box1 = tkinter.Frame(box)
        box2 = tkinter.Frame(box)

        lab1 = tkinter.Label(box1, text='原始路径：')
        lab2 = tkinter.Label(box2, text='修改路径：')
        self.tex1 = ScrolledText(box1, width=0, height=0) # width/height=0保证窗口拉伸时比例始终为1
        self.tex2 = ScrolledText(box2, width=0, height=0)
        lab1.pack(side='top', anchor='w')
        lab2.pack(side='top', anchor='w')
        self.tex1.pack(fill='both', side='left', expand=True)
        self.tex2.pack(fill='both', side='left', expand=True)

        btn1 = tkinter.Button(self, text='读取', command=self.load)
        btn2 = tkinter.Menubutton(self, text='标密', relief=tkinter.RAISED)
        btn3 = tkinter.Button(self, text='去标', command=self.unmark)
        btn4 = tkinter.Button(self, text='确认', command=self.rename)
        btn5 = tkinter.Button(self, text='撤回', command=self.rollback)

        self.menu = tkinter.Menu(btn2, tearoff=False)

        for rank in ranks:
            self.AddMenu(rank)
        self.menu.add_separator()
        self.btn2_var = tkinter.IntVar()
        self.menu.add_checkbutton(label='手动', command=self.edit, variable=self.btn2_var)
        btn2.config(menu=self.menu)
        
        box.pack(side='top', fill='both', expand=True)
        box1.pack(side='left', fill='both', expand=True)
        box2.pack(side='left', fill='both', expand=True)
        btn5.pack(side='right', fill='y')
        btn4.pack(side='right', fill='y')
        btn3.pack(side='right', fill='y')
        btn2.pack(side='right', fill='y')
        btn1.pack(side='right', fill='y')

        self.tex1.config(bg='#FFFFFF') # 有时系统设置会覆盖默认的白色(比如护眼绿色)
        self.tex2.config(state='disabled', bg='#F0F0F0') # 禁止编辑

        setCenter(self)
        self.deiconify()


    def AddMenu(self, rank):
        self.menu.add_command(label=rank, command=lambda:self.mark(rank)) # add_radiobutton会有个打钩造成歧义(不确定当列表更新后是否需要重新点击)


    def GetTexts(self):
        text1 = self.tex1.get('1.0', 'end')[:-1].split('\n')
        text2 = self.tex2.get('1.0', 'end')[:-1].split('\n')
        return text1, text2


    def SetText2(self, s):
        self.tex2.config(state='normal')
        self.tex2.delete('1.0', 'end')
        self.tex2.insert('1.0', s)
        self.tex2.config(state='disabled', bg='#F0F0F0') # 禁止编辑
        self.btn2_var.set(0) # 取消标记"手动"


    def load(self):
        files = tkinter.filedialog.askopenfilenames()
        if files:
            if self.tex1.get('1.0', 'end') != '\n': # Text为空时不在前面增加\n
                self.tex1.insert('end', '\n')
            self.tex1.insert('end', '\n'.join(files))


    def edit(self):
        if self.btn2_var.get():
            tkinter.messagebox.showinfo('提示', '您现在选中的是手动编辑功能，右侧文文本栏可以进行编辑。将对左侧的每一行路径，重命名为右侧文本对应行的路径和文件名，请谨慎确认对应正确后操作。选择其他模式后自动退出。')
            self.tex2.config(state='normal', bg='#ffffff')
        else:
            self.tex2.config(state='disabled', bg='#F0F0F0') # 禁止编辑


    def mark(self, rank='内部'):
        if rank in ['机密','绝密']:
            ret = tkinter.messagebox.askyesno('确认', '您现在选择的批量标密密级是【%s】，您确定要对文件批量标定为【%s】密级吗？点“否”请重新选择。'%(rank, rank))
            if not ret:
                return
        paths1 = self.GetTexts()[0]
        paths2 = MarkFiles(paths1, rank)
        self.SetText2('\n'.join(paths2))


    def unmark(self):
        ret = tkinter.messagebox.askyesno('确认', '去标功能将去除文件名中的密级标记，当密级标记前后存在括号将一并去除。是否需要进行该操作？')
        if not ret:
            return
        paths1 = self.GetTexts()[0]
        paths2 = UnmarkFiles(paths1)
        self.SetText2('\n'.join(paths2))


    def rename(self):
        RenameFiles(*self.GetTexts())


    def rollback(self):
        ret = tkinter.messagebox.askyesno('确认', '撤回功能通常应对于对密级错误标记的撤回操作，实现功能为将右侧的文件列表重命名为左侧对应的文件列表路径。是否需要进行该操作？')
        if not ret:
            return
        RenameFiles(*reversed(self.GetTexts()))



top = myPanel()
top.mainloop()

