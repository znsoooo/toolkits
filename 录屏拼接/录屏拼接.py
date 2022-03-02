import os
import sys
import time

import cv2
import numpy as np


METHOD = cv2.TM_SQDIFF_NORMED # TM_SQDIFF_NORMED, TM_CCORR_NORMED, TM_CCOEFF_NORMED


def unique(p, dash='-'):
    '''命名唯一文件名'''
    root, ext = os.path.splitext(p)
    n = 0
    while os.path.exists(p):
        n += 1
        p = '%s%s%d%s' % (root, dash, n, ext)
    return p


def diff(arr1, arr2): # for test
    '''比较两数组之间的差异'''
    result = []
    for n, (a1, a2) in enumerate(zip(arr1, arr2)):
        if a1 != a2:
            result.append(f'{n:3}: {a1:3}, {a2:3}')
    return '\n'.join(result)


def imshow(img, delay=50, title=''): # for test
    '''显示图像'''
    cv2.imshow(title, img)
    cv2.waitKey(delay)


def imsave(file): # for test
    '''保存视频所有帧为图片'''
    folder = os.path.splitext(file)[0]
    os.makedirs(folder, exist_ok=True)
    for n, img in enumerate(imiter(file)):
        cv2.imwrite(f'{folder}/img_{n:04}.png', img)


def imiter(file, st=None, ed=None):
    '''封装的视频读取迭代器'''
    cap = cv2.VideoCapture(file)
    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            cap.release()
            return
        yield img[st:ed]


def repeat(file):
    '''计算视频中存在变化的区域起止范围'''
    data = []
    for img in imiter(file):
        h, w, n = img.shape
        data.append(img.reshape((h, -1)).mean(1))
    data = np.array(data)
    var = data.var(0)
    where = np.where(var > var.mean())[0]
    return where.min(), where.max() + 1


def match(image, templ, method):
    th, tw = templ.shape[:2]
    result = cv2.matchTemplate(image, templ, method)
    result2 = (result - result.min()) / (result.max() - result.min())
    # imshow(np.tile(result2, 150)) # for debug
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return min_loc if method == cv2.TM_SQDIFF_NORMED else max_loc


def offset(img1, img2):
    '''计算两张图片的平移偏移量'''
    img2 = img2[100:-img2.shape[0]//2] # 搜寻范围
    dh = match(img1, img2, METHOD)
    return dh[1] - 100


def calc(file, st=None, ed=None):
    '''计算纵向滚动视频的逐帧偏移量'''
    gaps = []
    for n, img2 in enumerate(imiter(file, st, ed)):
        if n:
            dh = offset(img1, img2)
            gaps.append(dh)
        img1 = img2
    return gaps


def join_bottom(file, gaps, st=None, ed=None): # TODO 只能<向下>拼接
    '''滚动拼接到图片底部'''
    imgs = imiter(file, st, ed)
    data = next(imgs)
    for n, (img, gap) in enumerate(zip(imgs, gaps)):
        data = np.concatenate([data, img[img.shape[0] - gap:]])
    return data


def join_avg(file, gaps, st=None, ed=None):
    '''加权拼贴图像'''
    imgs = imiter(file, st, ed)
    data = next(imgs).astype(np.int16)
    data = np.concatenate([data, np.zeros((sum(gaps), *data.shape[1:]), np.int16)]) # 扩展填0
    weight = np.zeros_like(data)
    height = data.shape[0]
    st = 0
    for n, (img, gap) in enumerate(zip(imgs, gaps)):
        st += gap
        ed = min(height, st + img.shape[0])
        data  [st:ed] += img[:ed-st]
        weight[st:ed] += np.ones_like(img[:ed-st])
    return data // weight


def video2picture(file):
    '''视频转长图并自动保存'''
    # imsave(file) # for test
    # for img in imiter(file):
    #     imshow(img)

    if not 'easy':
        gaps = calc(file)
        data = join_bottom(file, gaps)

    else:
        st, ed = repeat(file)
        # st, ed = (None, None)
        print('st, ed =', (st, ed))
        gaps = calc(file, st, ed) # TODO 不掐头去尾反而更准确一点，因为有“惩罚”
        print('gaps =', gaps)

        if 'avg':
            data = join_avg(file, gaps, st, ed)
        else:
            data = join_bottom(file, gaps, st, ed)

    file2 = unique(file.rsplit('.')[0] + '.png')
    cv2.imwrite(file2, data)


if __name__ == '__main__':
    '''带参数打开视频作为输入'''
    if len(sys.argv) == 1:
        video2picture('video.mp4')
    else:
        for file in sys.argv[1:]:
            video2picture(file)
