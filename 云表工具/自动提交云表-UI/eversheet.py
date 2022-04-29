# build 20200604
# 登录云表并复制最后一次提交的<保密自查表>并重复提交新一月的表单

# 20210203
# 时间基准改为定位为20天前的日期
# 支持修改保密次数和保密学时(字段s_1_4_1和s_1_4_2)

# feature:
# 自动获取当前用户名填充为账号
# 默认填充当前年份和月份
# 本地存储用户自定义信息
# 确认提交信息并允许更改
# input确认信息是否正确 -- [y/n]确认
# 默认不更改和输入新值修改的写法 -- new = input(hint) or origin
# 多电脑拷贝自动辨认主机发生变化(通过获取本机MAC地址)

# debug打包:
# 避免pyinstaller打包成debug模式时产生报错(-d noarchive)
# 避免debug运行时程序运行结束自动退出(Press Enter to finish)

import os
import json
import time
import hashlib
import urllib.request

appName = '00caee91-e487-48a2-a834-85430b495bb6'
appKey  = 'eef3cd0d-fbc2-4645-9a6a-969c6251aa3d'

BASE_URL = 'http://10.110.0.177:88/10002/openapi/1.0/'

headers = {}


#---------------------------------------------------------------------------
# 云表
#---------------------------------------------------------------------------


def dumps(data):
    res = json.dumps(data, ensure_ascii=0, indent=2)
    return res


def md5(s):
    return hashlib.md5(s.encode()).hexdigest().upper()


def request(relative_path, data=None):
    url = BASE_URL + urllib.parse.quote_plus(relative_path).replace('%2F', '/')
    request  = urllib.request.Request(url, headers=headers, data=data)
    response = urllib.request.urlopen(request, timeout=30)
    content  = response.read().decode()
    data = json.loads(content)
    return data


def pack(name, data):
    data = json.dumps(data).replace(' ', '')
    data = name+'='+urllib.parse.quote_plus(data)
    return data.encode()


def login(username, password):
    ttime = str(int(time.time()*1000))
    Sign  = md5(ttime + appKey)

    global headers
    headers = {'x-eversheet-request-sign': Sign + ',' + ttime,
               'Content-Type': 'application/x-www-form-urlencoded',
               'x-eversheet-application-name': appName}

    data = {'account': username, 'password': md5(password)}
    loginJson = request('login', data=pack('loginJson', data))
    headers['token'] = loginJson['token']

    return headers, loginJson


#---------------------------------------------------------------------------


def AnalysisLoginJson(loginJson):
    print('你好: %s %s'%(loginJson['departmentName'], loginJson['user']))


def AnalysisPageJson(data):
    result = ['%s,%s,%s'%(row['objectId'], row['updatedAt'], row['createdBy']) for row in data['results']]
    return '\n'.join(result)


#---------------------------------------------------------------------------
# 获取待提交用户信息
#---------------------------------------------------------------------------


def GetDefault():
    import re
    import uuid
    import getpass
    import datetime

    mac      = '-'.join(re.findall('..', uuid.uuid1().hex[-12:].upper()))
    user     = getpass.getuser()
    username = user + '@12.calt.casc'
    password = '123456'
    day_base = datetime.date.today() - datetime.timedelta(days=20) # 定位为20天前的日期
    year     = day_base.year
    month    = day_base.month

    return [mac, username, password, year, month]


def GetSaved(file):
    if not os.path.exists(file):
        open(file, 'w').close()
    with open(file) as f:
        s = f.read()
    return (s + '\n\n').split('\n')[:3]  # mac, username, password


def GetUserData(file):
    user_default = GetDefault()
    user_saved   = GetSaved(file)
    if user_saved[0] == user_default[0]:
        print('读取用户信息成功')
        user_data = user_saved + user_default[-2:]  # year, month
    else:
        print('本机第一次使用，自动生成默认信息')
        user_data = user_default
    return user_data  # mac, username, password, year, month


def SaveUserData(file, data):
    with open(file, 'w') as f:
        f.write('\n'.join(map(str, data)))  # mac, username, password


def history(username, password):
    # 登录
    try:
        headers, loginJson = login(username, password)
        AnalysisLoginJson(loginJson)
    except:
        return '登录失败，请检查用户名和密码输入是否正确。'

    # 获取总表
    data = request('十二所员工月度保密自查表')
    data = [(row['自查年'], row['自查月']) for row in data['results'] if row['人员账户'] == username]
    data = [f'{y}年{m}月' for y, m in data]

    return '已填：\n' + '\n'.join(data)
    

def submit(username, password, year, month, n1, n2):
    # 登录
    try:
        headers, loginJson = login(username, password)
        AnalysisLoginJson(loginJson)
    except:
        return '登录失败，请检查用户名和密码输入是否正确。'

    # 获取总表
    data = request('十二所员工月度保密自查表')
    for row in data['results']:
        if row['人员账户'] == username:
            break
    latest_id = row['objectId']
    print('获取列表:')
    print(AnalysisPageJson(data))
    print('latest_id: %s'%latest_id)

    # 获取历史提交数据
    data = request('十二所员工月度保密自查表/%s'%latest_id)
    print('获取表单:')
    print(dumps(data))

    # 提交数据
    data['objectId'] = 0
    data['自查年'] = year
    data['自查月'] = month

    # 修改保密次数和保密学时(字段s_1_4_1和s_1_4_2)
    data['s_1_4_1'] = n1
    data['s_1_4_2'] = n2

    try:
        request('十二所员工月度保密自查表/%s'%latest_id, data=pack('formJson', data))
        return '提交成功，请登录云表网页版查看确认信息正确。'
    except:
        return '填写失败，请确认需要提交的"自查年"和"自查月"信息是否正确，如果当月记录已经存在则不能重复提交！'


if __name__ == '__main__':
    mac, username, password, year, month = GetUserData('user.txt')
    print(mac, username, password, year, month)
    ret = submit(username, password, 2022, 3, 1, 1)
    print(ret)
