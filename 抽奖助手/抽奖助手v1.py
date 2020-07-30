# build 20200724

import time
import random
import tkinter
import tkinter.font
from threading import Thread

is_run = 1
mode = -1 # -1: start; 0: run; 1: stop
result = []

def shuffle():
    while is_run:
        while is_run and mode:
            pass
        time.sleep(0.05)
        if not mode:
            random.shuffle(namelist)
            t1.config(text=namelist[0])
        else:
            result.append(namelist.pop())
            t1.config(text=result[-1])
            t2.config(text='抽中结果：%s、…'%'、'.join(result))

def switch(evt):
    global mode
    mode = not mode # -1 -> 0 -> 1 -> 0 -> 1 -> ...

with open('namelist.csv') as f:
    namelist = list(filter(bool, set(f.read().split('\n'))))
    print(len(namelist))

top = tkinter.Tk()
top.title('抽奖助手')
top.state('zoomed')
##top.attributes('-fullscreen', True)
top.config(bg='#000000')
top.bind('<space>', switch)

ft = tkinter.font.Font(size=240, family='黑体')
t1  = tkinter.Label(top, text='抽奖助手', font=ft)
t2 = tkinter.Label(top, anchor='w')
t1.pack(expand=1, fill='both') # 延伸文本框宽度防止字体内容刷新时导致闪烁
t2.pack(expand=1, fill='both', side='left')

t1.config(bg='#000000', fg='#88FF88')
t2.config(bg='#000000', fg='#FFFFFF')

Thread(target=shuffle).start()

top.mainloop()

is_run = 0
