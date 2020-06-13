import cv2
import numpy as np


def ReadVideo(file):
    # debug
##    img = cv2.imread('last-blur-origin.png')
##    yield img
##    return
    # debug
    cap = cv2.VideoCapture(file)
    while 1:
        ret, img = cap.read()
        if not ret:
            cap.release()
            break
        yield img


def GetContours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    binary, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return reversed(contours) # contours: 从下到上 从右到左顺序


def Get4Points(contour, draw=False):
    approx = cv2.approxPolyDP(contour, 3, True) # approx: y最小者第一 逆时针顺序

    tl = tr = bl = br = tuple(approx[0][0])
    for [[x1, y1]] in approx[1:]:
        if x1 + y1 < (tl[0] + tl[1]):
            tl = (x1, y1)
        if x1 + y1 > (br[0] + br[1]):
            br = (x1, y1)
        if x1 - y1 < (bl[0] - bl[1]):
            bl = (x1, y1)
        if x1 - y1 > (tr[0] - tr[1]):
            tr = (x1, y1)

    if draw:
        cv2.polylines(img, [approx], True, (0, 255, 0), 2)
        cv2.circle(img, tl, 1, (0, 0, 255), 25)
        cv2.circle(img, tr, 1, (0, 255, 255), 25)
        cv2.circle(img, bl, 1, (0, 255, 0), 25)
        cv2.circle(img, br, 1, (255, 0, 0), 25)

    return tl, tr, bl, br


def ImgToQr(img, points, edge=104, offset=((2,2),(2,2),(2,2),(2,2))):
    tl, tr, bl, br = points
    point1 = (np.array([tl,tr,bl,br]) + offset).astype('float32')
    point2 = np.array([[0,0],
                       [edge,0],
                       [0,edge],
                       [edge,edge]], dtype='float32')
    M = cv2.getPerspectiveTransform(point1, point2)
    img_qr_sq = cv2.warpPerspective(img, M, (edge,edge))
    img_qr_gray = cv2.cvtColor(img_qr_sq, cv2.COLOR_RGB2GRAY)
    ret, img_qr_thresh = cv2.threshold(img_qr_gray, 127, 255, cv2.THRESH_BINARY)

    return img_qr_gray



B2D = np.array([128,64,32,16,8,4,2,1])
offset_list = [((2, 2), (2, 2), (2, 2), (2, 2)),
               ((2, 1), (2, 2), (2, 2), (2, 2)),
               ((1, 2), (2, 2), (2, 2), (2, 2)),
               ((1, 2), (2, 2), (1, 2), (2, 2)),
               ((2, 1), (2, 2), (2, 2), (2, 1)),
               ((1, 1), (2, 2), (1, 2), (2, 2)),
               ((1, 1), (2, 2), (2, 2), (2, 2)),
               ((2, 2), (2, 2), (1, 2), (2, 2)),
               ((2, 1), (2, 2), (1, 2), (2, 2))
               ]
##((2, 2), (2, 2), (2, 2), (2, 2))	82	8.87%
##((2, 1), (2, 2), (2, 2), (2, 2))  	75	8.12%
##((1, 2), (2, 2), (2, 2), (2, 2))  	59	6.39%
##((1, 2), (2, 2), (1, 2), (2, 2))  	48	5.19%
##((2, 1), (2, 2), (2, 2), (2, 1))  	45	4.87%
##((1, 1), (2, 2), (1, 2), (2, 2))  	39	4.22%
##((1, 1), (2, 2), (2, 2), (2, 2))  	39	4.22%
##((2, 2), (2, 2), (1, 2), (2, 2))  	38	4.11%
##((2, 1), (2, 2), (1, 2), (2, 2))  	36	3.90%
##((1, 2), (2, 2), (2, 2), (1, 2))  	20	2.16%
##((1, 1), (2, 2), (2, 2), (1, 2))  	18	1.95%
##((2, 0), (2, 2), (2, 2), (2, 2))  	16	1.73%
##((1, 2), (2, 1), (1, 2), (2, 2))  	15	1.62%
##((2, 2), (2, 2), (2, 2), (2, 1))  	14	1.52%
##((1, 2), (2, 2), (1, 2), (1, 2))  	12	1.30%
##((2, 1), (2, 2), (2, 2), (1, 2))  	12	1.30%
##((1, 0), (2, 2), (2, 2), (2, 2))  	11	1.19%
##((0, 1), (2, 2), (2, 2), (2, 2))  	10	1.08%


def bin2dec(arr):
    return sum(qr_data[0]*B2D)


cnt1 = cnt2 = 0

file = 'VID_20191124_084544.mp4'
data = []
for frame, img in enumerate(ReadVideo(file)):
    print('read frame: %s'%frame)
##    print(cnt1, cnt2, cnt2/(cnt1+cnt2+1))
    for cnt, contour in enumerate(GetContours(img)):
        # print('read: %s/%s'%(frame, cnt))
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 100:
            points = Get4Points(contour)  # 得到四角定点
            qr_img = ImgToQr(img, points) # 转正后的二维码

##            var = 0
##            offset = 0
##            for i in range(3**8):
##                a = np.array(i).repeat(8) // [3**7,3**6,3**5,81,27,9,3,1] % ([3]*8)
##                qr_img1 = ImgToQr(img, points, offset=((a[0],a[1]),(a[2],a[3]),(a[4],a[5]),(a[6],a[7])))
##                if qr_img1.var() > qr_img.var():
##                    qr_img = qr_img1
##                    var = qr_img1.var()
##                    offset = ((a[0],a[1]),(a[2],a[3]),(a[4],a[5]),(a[6],a[7]))
##            print(offset, var)

            var = qr_img.var()
            for offset in offset_list:
                qr_img1 = ImgToQr(img, points, offset=offset)
                if qr_img1.var() > qr_img.var():
                    qr_img = qr_img1
                    var = qr_img1.var()

                
            qr_data = (qr_img>127)[2:102, 2:102].reshape((-1,8))*1 # 255转为True 去除白色边框 变形8位一组 转为int

            serial = sum(qr_data[0]*B2D)*256+sum(qr_data[1]*B2D) # 二维码序列编号(前16个bit)
            # print('serial: %s'%serial)

            if serial + 1 > len(data):
                for i in range(serial + 1 - len(data)):
                    data.append(0)

            data[serial] += qr_data # 多帧读取结果累加防止错判 其中无视元素初始值等于0不会出错
            # print('data: %s'%data)

##
            if var < 4000:
                print(frame, cnt, var)

                b = 20
                # cv2.imshow('lsx', img[y-b:y+h+b, x-b:x+w+b])
                cv2.imwrite('var/%d-f%d-n%d-original.png'%(var, frame, cnt), img[y-b:y+h+b, x-b:x+w+b])
                cv2.waitKey(0)

                qr_img_zoom = cv2.resize(qr_img, (qr_img.shape[0]*5, qr_img.shape[1]*5), interpolation=cv2.INTER_NEAREST)
                # cv2.imshow('lsx', qr_img_zoom)
                cv2.imwrite('var/%d-f%d-n%d.png'%(var, frame, cnt), qr_img_zoom)
                # cv2.waitKey(0)

cv2.destroyAllWindows()



# 取平均清洗所有数据
for serial in range(len(data)):
    if data[serial] is not 0:
        unfold = data[serial].reshape(-1)
        average = (max(unfold) + min(unfold)) / 2
        data[serial] = sum(((data[serial]>average)*B2D).T) # 多次结果取平均 对应位加权 转置比特中的8个字节求和
        data[serial] = (max(unfold), data[serial])


cnt = 0
data_real= []
for serial, qr_data in enumerate(data):
    # 按序号读取所有数据,空白补0
    if qr_data is 0:
        qr_data = np.zeros(1250, np.int)
        repeat = 0
        print('empty:', serial)
    else:
        repeat, qr_data = qr_data
    data_real.append(qr_data)

    # 疑似无效数据计数
    if repeat < 3:
        cnt += 1
    else:
        cnt = 0

    # 连续5次出现疑似无效数据认为数据截止
    if cnt == 5:
        break

print(cnt, len(data_real))

data_real = list(np.array(data_real[:-5])[:,2:].reshape(-1)) # 排除最后5次 转为np数组 去掉计数位 展为1维数组 转为list(否则转换bytes时1个数字占用不止1个字符)


with open('output_20200302_5.rar', 'wb') as f:
    f.write(bytes(data_real[:2326994]))

end = b'\x00\xff\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f'
# file size: 2326994

# 至少3组数据认为可信 (TODO: 有失败的)


# frame: 688
# 使用内存约400MB
