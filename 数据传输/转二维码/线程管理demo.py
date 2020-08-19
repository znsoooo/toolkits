# 20200819 build

import time
import random
from threading import Thread

th_max = 10 # 最大线程数

th_arr = [] # 运行中线程
th_fin = [] # 已完成线程


class MyThread(Thread):
    def __init__(self, func, args=()):
        Thread.__init__(self)
        self.func = func
        self.args = args
        self.start()

    def run(self):
        self.result = self.func(*self.args)
        th_fin.append(self) # 先append后remove防止接力失败时两个数组均为空(尾部程序判断时误判)
        th_arr.remove(self)


def MyFunction(a, b): # 后台线程运行程序
    time.sleep(random.randint(800, 1300)/1000) # 模拟程序实际运行耗时不同
    return a + b


def JoinResult(data): # 对线程处理结果进行管理
    print('Result: %s'%data)


if __name__ == "__main__":
    for i in range(100):
        print('Input: %s'%i)

        while len(th_arr) >= th_max:
            pass
        th_arr.append(MyThread(MyFunction, (i, i*2)))

        while th_fin:
            JoinResult(th_fin.pop().result)

    while th_arr or th_fin:
        if th_fin:
            JoinResult(th_fin.pop().result)
