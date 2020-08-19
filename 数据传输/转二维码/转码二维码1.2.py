# 20191119
# Ver 1.0

# 20200226
# 转为基于numpy和cv2运算的程序,大幅降低了运行速度

import cv2
import time
import numpy as np

import tkinter

top = tkinter.Tk()
SCREEN_WIDTH  = top.winfo_screenwidth()
SCREEN_HEIGHT = top.winfo_screenheight()
top.destroy()


D2B = np.array([128,64,32,16,8,4,2,1])

def expand(img, dh, dw, fill=0):
    h, w = img.shape[:2]
    bg = np.zeros((h+dh*2, w+dw*2), np.uint8)
    if fill:
        bg.fill(fill)
    bg[dh:-dh,dw:-dw] = img

    return bg

def bytes2bits(byte):
    return (((np.array(list(byte)).repeat(8).reshape(-1,8)&D2B)>0))

def string2qr(string, rect, width=2):
    w, h = rect
    img = bytes2bits(string).astype(np.uint8).reshape(h,w)*255

    img = expand(img, 2, 2, 255)
    img = expand(img, 3, 3)
    img = img.repeat(width, axis=0).repeat(width, axis=1)
    
    return img


def data2qrs(file, rect, mat, width):
    cv2.namedWindow('lsx', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty('lsx', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    w, h = rect
    r, c = mat
    mat_n = r * c
    length = int(w * h / 8) - 2 # 2位是计数
    cnt = 0
    first = True
    with open(file, 'rb') as f:
        while 1:
            string = f.read(length * mat_n)
            if len(string) == 0:
                break
            elif len(string) < length * mat_n:
                string = string + b'\x00\xff' + b'\x0f' * (length * mat_n - len(string) - 2)

            string_data = np.array(list(string)).reshape(-1, length)
            serials = np.array(divmod(np.arange(cnt, cnt + mat_n), 256))
            page_data = np.insert(string_data, 0, serials, axis=1)
            cnt += mat_n
            # print(page_data)

            page_data = page_data.reshape(r, c, length + 2)
            page = np.array([[string2qr(cell_string, rect, width) for cell_string in row] for row in page_data])
            page2 = np.concatenate(np.concatenate(page, axis=1), axis=1)
            page3 = expand(page2, int((SCREEN_HEIGHT-page2.shape[0])/2), int((SCREEN_WIDTH-page2.shape[1])/2))

            cv2.imshow('lsx', page3)
            if cv2.waitKey(1) == 27: # ESC
                break

            if first:
                cv2.waitKey(0)
                first = False


data2qrs('passage2019.rar', (400, 200), (1, 1), 4)

cv2.waitKey(0)
cv2.destroyAllWindows()

