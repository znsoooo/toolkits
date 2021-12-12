# build 20200817
# 第一次使用assert
# 打乱顺序读取root文件夹内的子文件夹，点击左右前进后退浏览图片，点击回车打开所在文件夹

import os
import random
import tkinter
from PIL import Image, ImageTk

join = os.path.join

root = 'image'

fods1 = os.listdir(root)
random.shuffle(fods1)
fods2 = []

imgs1 = []
imgs2 = []

def center(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

def next(evt=0):
    try:
        imgs2.append(imgs1.pop())
    except:
        fods2.append(fods1.pop())
        imgs1.extend(list(reversed(os.listdir(join(root, fods2[-1])))))
        imgs2.clear()
        imgs2.append(imgs1.pop())
    try:
        show()
    except:
        next()

def prev(evt=0):
    try:
        imgs1.append(imgs2.pop())
        assert imgs2
    except:
        fods1.append(fods2.pop())
        imgs2.extend((os.listdir(join(root, fods2[-1]))))
        imgs1.clear()
    try:
        show()
    except:
        prev()

def show():
    global img
    path = join(root, fods2[-1], imgs2[-1])
    img = ImageTk.PhotoImage(Image.open(path))
    lab.config(image=img)
    top.title(path)
    center(top)

def enter(evt):
    os.popen('explorer /select, ' + join(root, fods2[-1], imgs2[-1]))


top = tkinter.Tk()
lab = tkinter.Label(top)
lab.pack()
top.bind('<Left>', prev)
top.bind('<Right>', next)
top.bind('<Return>', enter)
next()
top.mainloop()
