# TODO
# 整体try
# 删除生成的临时文件

import os
import re
import zipfile
from win32com import client

def file2text(path):
    root, ext = os.path.splitext(path)
    ret = None
    if ext == '.doc':
        word = client.Dispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.SaveAs(root + '.temp.docx', 16)
        doc.Close()
        ret, ss = file2text(root + '.temp.docx')
    elif ext == '.xls':
        excel = client.Dispatch('Excel.Application')
        excel.DisplayAlerts = False # 否则会有文件保存提示
        xls = excel.WorkBooks.Open(path)
        xls.SaveAs(root + '.temp.xlsx', 51)
        xls.Close()
        ret, ss = file2text(root + '.temp.xlsx')
    elif ext == '.ppt':
        powerpoint = client.Dispatch('PowerPoint.Application')
        # powerpoint.Visible = 1
        ppt = powerpoint.Presentations.Open(path, WithWindow=0) # 没有WithWindow=0导致PPT无法打开,虽然可以增加powerpoint.Visible=1以打开,但是会导致读取时会启动窗口
        ppt.SaveAs(root + '.temp.pptx')
        ppt.Close()
        ret, ss = file2text(root + '.temp.pptx')
    elif ext == '.docx':
        f = zipfile.ZipFile(path, 'r')
        s = f.read('word/document.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<w:pPr>','\n'))
    elif ext == '.xlsx':
        f = zipfile.ZipFile(path, 'r')
        s = f.read('xl/sharedStrings.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<si>','\n'))
    elif ext == '.pptx':
        f = zipfile.ZipFile(path, 'r')
        files = f.namelist()
        s = ''
        max_page = 0
        for file in files:
            if file[:16] == 'ppt/slides/slide':
                max_page = max_page + 1
        for i in range(max_page):
            file = 'ppt/slides/slide%s.xml'%(i+1)
            s = s + file + f.read(file).decode() + '\n\n'
        s = s.replace('<a:p>','\n')
        s = re.sub(r'<p:attrName>.*?</p:attrName>','',s)
        ss = re.sub(r'<.*?>','',s)
    else:
        with open(path, 'rb') as f:
            ss = f.read()
        try:
            ss = ss.decode()
        except:
            try:
                ss = ss.decode('gbk') #, errors='replace')
            except Exception as e:
                ss = re.sub(rb'[\0-\10\13\14\16-\37]+', b' ', ss).decode(errors='ignore')#[:10000]
                ret = str(e)

    return ret, ss

if __name__ == '__main__':
    files = os.listdir('demo')
    for file in files:
        ret, ss = file2text(os.path.join(os.getcwd(),'demo',file))
        print('='*80)
        print(file, ret, ss[:200])

