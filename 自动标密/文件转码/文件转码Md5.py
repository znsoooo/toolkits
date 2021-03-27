# build 20210325

import os
import time
import hashlib

LOG = time.strftime('log/rollback_%Y%m%d_%H%M%S.bat')

def Md5(s):
    return hashlib.md5(s.encode()).hexdigest()

print('输入(多行)路径，转为Md5命名：')
cnt1 = cnt2 = 0
while 1:
    file = input('> ')
    os.makedirs('log', exist_ok=1)
    file2 = os.path.join(os.path.dirname(file), Md5(os.path.basename(file)))
    try:
        os.rename(file, file2)
        with open(LOG, 'a') as f:
            f.write('move "%s" "%s"\n'%(file2, file))
        cnt1 += 1
    except:
        cnt2 += 1
    print('成功%d个文件，失败%d个文件。'%(cnt1, cnt2))

