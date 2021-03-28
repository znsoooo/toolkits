# build 20210325
# fix 20210328
# 根据文件标题和格式映射对6种格式的office文档在文档内部左上角添加文本框文字
# 通过input函数模拟出按下Enter能实现粘贴文本的效果(实际上是获取剪切板)
# 操作情况保存带有时间戳的自动日志

print('文档内部标密工具v1.0')
print('联系方式QQ：11313213')
print('..')

import os
import time
import subprocess

import pyperclip
from win32com import client

INI = 'config.ini'
TXT = 'filelist.txt'


def Log(s):
    # ttime = time.strftime('[%Y-%m-%d %H:%M:%S] ')
    ttime = '[%4.1f] '%(time.time()-TIME)
    print(ttime + s)
    with open(LOG, 'a') as f:
        f.write(ttime + s + '\n')


def LoadRegular():
    if not os.path.exists(INI):
        with open(INI, 'w') as f:
            pass
    with open(INI) as f:
        s = f.read()
    regular = [line.split(',', 1) for line in s.split('\n') if ',' in line]
    return regular


def SetTextFrame(tf, text, kh=2, kv=3):
    tf.TextRange.Text = text
    tf.TextRange.ParagraphFormat.Alignment = kh
    tf.VerticalAnchor = kv
    tf.MarginLeft = 0
    tf.MarginRight = 0
    tf.MarginTop = 0
    tf.MarginBottom = 0
    

def AddTextbox(obj, pos):
    box = obj.Shapes.AddTextbox(1, *pos)
    box.Fill.Visible = True # 为了覆盖住以前的标密
    box.Line.Visible = True
    return box


def AddText(file, text, middle='.temp', pos=(20, 20, 100, 20)):
    path = os.path.abspath(file)
    root, ext = os.path.splitext(path)

    if ext in ['.doc', '.docx']:
        word = client.Dispatch('Word.Application')
        doc = word.Documents.Open(path)
        box = AddTextbox(doc, pos)
        SetTextFrame(box.TextFrame, text, kh=1)
        doc.SaveAs(root + middle + ext, 16)
        doc.Close()

    elif ext in ['.xls', '.xlsx']:
        excel = client.Dispatch('Excel.Application')
        excel.DisplayAlerts = False # 否则会有文件保存提示
        xls = excel.WorkBooks.Open(path)
        s1 = xls.Sheets(1)
        box = AddTextbox(s1, pos)
        SetTextFrame(box.TextFrame2, text)
        xls.SaveAs(root + middle + ext, 51)
        xls.Close()

    elif ext in ['.ppt', '.pptx']:
        powerpoint = client.Dispatch('PowerPoint.Application')
        # powerpoint.Visible = 1
        ppt = powerpoint.Presentations.Open(path, WithWindow=0) # 没有WithWindow=0导致PPT无法打开,虽然可以增加powerpoint.Visible=1以打开,但是会导致读取时会启动窗口
        s1 = ppt.Slides(1)
        box = AddTextbox(s1, pos)
        SetTextFrame(box.TextFrame2, text)
        ppt.SaveAs(root + middle + ext)
        ppt.Close()


print('加载规则文件"%s"：'%INI)
regular = LoadRegular()
print(regular)
print('..')

input('标密软件会根据规则匹配文件名中标注的密级，在文档内部左上角添加文本框进行标密。该操作不可撤回，请谨慎操作。确认并接受标密软件对文档进行操作请按回车：')
print('..')

while 1:
    # files = NotepadInput(TXT, HINT+'\n').split('\n')
    input('请将需要转换的(多行)文件路径复制，按回车粘贴：')
    files = pyperclip.paste().splitlines()
    files = [file.strip() for file in files if file.strip()]

    # input('请按回车开始转换，对%d个文档内部进行标密。该操作不可撤回，请谨慎操作：'%len(files))
    os.makedirs('log', exist_ok=1)
    LOG = time.strftime('log/RECORD_%Y%m%d_%H%M%S.log')

    print('..')
    print('开始转换..')
    TIME = time.time()
    success = []
    failed  = []
    for n, file in enumerate(files):
        if not os.path.isfile(file):
            Log('File not exist of "%s"'%(file))
            continue # 跳过非文件
        if os.path.splitext(file)[1] not in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            Log('Extension not available of "%s"'%(file))
            continue # 跳过后缀名不匹配

        basename = os.path.basename(file)
        for key, text in regular:
            if key in basename:
                try:
                    AddText(file, text , middle='') # , middle=''
                    success.append(file)
                    Log('(%d/%d) Success add "%s" in "%s"'%(n+1, len(files), text, file))
                except Exception as e:
                    failed.append(file)
                    Log('(%d/%d) Failed  add "%s" in "%s" error "%s"'%(n+1, len(files), text, file, e))
                break # 前面的规则优先级高
        else:
            Log('Mismatch keys in "%s"'%(file))
    print('转换完毕..')
    print('..')

    if files:
        print('保存日志："%s"。'%os.path.abspath(LOG))
        print('..')

    if failed:
        print('失败：\n' + '\n'.join(failed))
        print('..')

    print('总共%d个文件，成功%d个文件，失败%d个文件，跳过%d个文件。'%(len(files), len(success), len(failed), len(files)-len(success)-len(failed)))
    print('..')


'''
test\excel(秘密).xlsx
test\word（秘密）.docx
test\ppt（机密）.pptx
'''
