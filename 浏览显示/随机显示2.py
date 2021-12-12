import os
import random
import tkinter
from PIL import Image, ImageTk

root = 'image'

folders = os.listdir(root)
random.shuffle(folders)

def get_len(ptr1):
    return len(os.listdir(join1(ptr1)))

def join1(ptr1):
    return os.path.join(root, folders[ptr1])

def join2(ptr1, ptr2):
    return os.path.join(root,
                        folders[ptr1],
                        os.listdir(join1(ptr1))[ptr2]
                        )

def show(ptr1, ptr2):
    global img
    try:
        img = ImageTk.PhotoImage(Image.open(join2(ptr1, ptr2)))
        lab.config(image=img)
    except:
        pass

def prev(evt):
    global ptr1, ptr2, len2
    ptr2 -= 1
    if ptr2 == -1:
        ptr1 -= 1
        ptr2 = get_len(ptr1) - 1
        len2 = get_len(ptr1)
    show(ptr1, ptr2)

def next(evt):
    global ptr1, ptr2, len2
    ptr2 += 1
    if ptr2 == len2:
        ptr1 += 1
        ptr2 = 0
        len2 = get_len(ptr1)
    show(ptr1, ptr2)

def enter(evt):
    os.popen('explorer' + join1(ptr1))


ptr1 = 0
len2 = get_len(ptr1)
ptr2 = 0

top = tkinter.Tk()
lab = tkinter.Label(top)
lab.pack()
top.bind('<Left>', prev)
top.bind('<Right>', next)
top.bind('<Return>', enter)
next(1)
prev(1)
top.mainloop()
