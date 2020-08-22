# 20200614
# 支持读取文档中的media资源
# 其他流程优化

# TODO
# 整体try
# 删除生成的临时文件
# 奇怪的xlsx无法读取

import os
import re
import zipfile
from win32com import client

def file2text(path, save_media=False):
    root, ext = os.path.splitext(path)
    ret = None
    if ext in ['.docx', '.xlsx', '.pptx']:
        f = zipfile.ZipFile(path, 'r')
        if save_media:
            files = f.namelist()
            os.makedirs(root, exist_ok=1)
            for file in files:
                if 'media' in file:
                    zip_filename = os.path.split(file)[1]
                    if zip_filename: # 当file是文件夹时filename=''
                        with open(os.path.join(root, zip_filename), 'wb') as f2:
                            f2.write(f.read(file))
            os.popen('explorer %s'%root)

        if ext == '.docx':
            s = f.read('word/document.xml').decode()
            s = s.replace('<w:pPr>','\n')
        elif ext == '.xlsx':
            s = f.read('xl/sharedStrings.xml').decode()
            s = s.replace('<si>','\n')
        elif ext == '.pptx':
            files = f.namelist()
            s = ''
            max_page = 0
            for file in files:
                if file.startswith('ppt/slides/slide'):
                    slide = '# %s #'%file[11:-4]
                    s += slide + f.read(file).decode() + '\n\n'
            s = s.replace('<a:p>','\n')
            s = re.sub(r'<p:attrName>.*?</p:attrName>','',s)
        ss = re.sub(r'<.*?>','',s)
        f.close()
    elif ext == '.doc':
        word = client.Dispatch('Word.Application')
        doc = word.Documents.Open(path)
        doc.SaveAs(root + '.temp.docx', 16)
        doc.Close()
        ret, ss = file2text(root + '.temp.docx', save_media)
    elif ext == '.xls':
        excel = client.Dispatch('Excel.Application')
        excel.DisplayAlerts = False # 否则会有文件保存提示
        xls = excel.WorkBooks.Open(path)
        xls.SaveAs(root + '.temp.xlsx', 51)
        xls.Close()
        ret, ss = file2text(root + '.temp.xlsx', save_media)
    elif ext == '.ppt':
        powerpoint = client.Dispatch('PowerPoint.Application')
        # powerpoint.Visible = 1
        ppt = powerpoint.Presentations.Open(path, WithWindow=0) # 没有WithWindow=0导致PPT无法打开,虽然可以增加powerpoint.Visible=1以打开,但是会导致读取时会启动窗口
        ppt.SaveAs(root + '.temp.pptx')
        ppt.Close()
        ret, ss = file2text(root + '.temp.pptx', save_media)
    else:
        with open(path, 'rb') as f:
            ss = f.read()
        try:
            ss = ss.decode('gbk')
        except:
            try:
                ss = ss.decode() #, errors='replace')
            except Exception as e:
                ss = re.sub(rb'[\0-\10\13\14\16-\37]+', b' ', ss).decode(errors='ignore')#[:10000]
                ret = str(e)

    return ret, ss


if __name__ == '__main__':
    files = os.listdir('demo')
    for file in files:
        ret, ss = file2text(os.path.join(os.getcwd(),'demo',file))
        print('='*20)
        print(file, ret, ss[:200])

