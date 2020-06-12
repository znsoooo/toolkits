import tkinter
import tkinter.constants as CON
import tkinter.filedialog

import os
import re
import difflib
import zipfile
from win32com import client

import compare

def file2text(file):
    extension = file.split('.')[-1]
    if file == '':
        ss = ''
    elif extension == 'doc':
        word = client.Dispatch('Word.Application')
        path = os.getcwd() + '\\'
        doc = word.Documents.Open(path + file)
        doc.SaveAs(path + file + '.temp.docx', 16)
        doc.Close()
        ss = file2text(file + '.temp.docx')
    elif extension == 'xls':
        excel = client.Dispatch('Excel.Application')
        path = os.getcwd() + '\\'
        xls = excel.WorkBooks.Open(path + file)
        xls.SaveAs(path + file + '.temp.xlsx', 51)
        xls.Close()
        ss = file2text(file + '.temp.xlsx')
    elif extension == 'ppt':
        powerpoint = client.Dispatch('PowerPoint.Application')
        powerpoint.Visible = 1
        path = os.getcwd() + '\\'
        ppt = powerpoint.Presentations.Open(path + file)
        ppt.SaveAs(path + file + '.temp.pptx')
        ppt.Close()
        ss = file2text(file + '.temp.pptx')
    elif extension == 'docx':
        f = zipfile.ZipFile(file,'r')
        s = f.read('word/document.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<w:pPr>','\r\n'))
    elif extension == 'xlsx':
        f = zipfile.ZipFile(file,'r')
        s = f.read('xl/sharedStrings.xml').decode()
        ss = re.sub(r'<.*?>','',s.replace('<si>','\r\n'))
    elif extension == 'pptx':
        f = zipfile.ZipFile(file,'r')
        files = f.namelist()
        s = ''
        max_page = 0
        for file in files:
            if file[:16] == 'ppt/slides/slide':
                max_page = max_page + 1
        for i in range(max_page):
            file = 'ppt/slides/slide%s.xml'%(i+1)
            s = s + file + f.read(file).decode() + '\n\n'
        ss = re.sub(r'<.*?>','',s.replace('<a:p>','\r\n'))
    else:
        with open(file, 'rb') as f:
            ss = f.read()
        try:
            ss = ss.decode()
        except:
            try:
                ss = ss.decode('gbk')
            except:
                # ss = str(ss)
                ss = ss

    return ss

def getResult(files, key):
    exist_files = [os.path.isfile(files[0]),
                   os.path.isfile(files[1]),
                   os.path.isfile(files[2])]
    exist_cnt = exist_files.count(True)
    print(exist_cnt)
    if exist_cnt == 0:
        res = '没有有效的文件。'
    elif exist_cnt == 1:
        for i in range(3):
            if exist_files[i]:
                res = file2text(files[i])
    elif exist_cnt == 2:
        if exist_files[0] == False:
            s1 = file2text(files[1]).splitlines()
            s2 = file2text(files[2]).splitlines()
            res = '\n'.join(compare.removeDiff(s1, s2, reverse=True))
        elif exist_files[1] == False:
            s1 = file2text(files[0]).splitlines()
            s2 = file2text(files[2]).splitlines()
            res = '\n'.join(compare.removeDiff(s1, s2))
        elif exist_files[2] == False:
            s1 = file2text(files[0]).splitlines()
            s2 = file2text(files[1]).splitlines()
            res = '\n'.join(compare.makeDiff(s1, s2))
    elif exist_cnt == 3:
        res = '文件名冲突。'
    return res

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.tex1 = tkinter.Text(self)
        self.tex1.pack(padx=2, pady=2, fill=CON.BOTH, side=CON.BOTTOM, expand=True)

        self.ss = []
        for i, bt_name in enumerate(['参照','对比','差异']):
            s = tkinter.StringVar()
            ent = tkinter.Entry(self, textvariable=s)
            btn = tkinter.Button(self, text=bt_name, command=lambda key=i:self.onButton(key))
            ent.bind('<KeyRelease>', lambda evt,key=i:self.onKeyRelease(evt,key))
            ent.pack(padx=2, pady=2, fill=CON.X, side=CON.LEFT, expand=True)
            btn.pack(padx=2, pady=2, fill=CON.X, side=CON.LEFT)
            self.ss.append(s)
            if i == 0:
                ent.focus()

        setCenter(self)

    def getFiles(self):
        return [self.ss[0].get(),
                self.ss[1].get(),
                self.ss[2].get()]

    def onButton(self, key):
        initialdir = os.path.dirname(self.ss[key].get())
        files = self.getFiles()
        exist_files = [os.path.isfile(files[0]),
                       os.path.isfile(files[1]),
                       os.path.isfile(files[2])]
        exist_cnt = exist_files.count(True)
        if exist_cnt == 2: # 打开文件和另存文件
            path = tkinter.filedialog.asksaveasfilename(initialdir=initialdir, filetypes=[('纯文本', '*.txt')])
        else:
            path = tkinter.filedialog.askopenfilename(title='qqq', initialdir=initialdir)
        if path != '':
            self.ss[key].set(path)
        res = self.onKeyRelease(-1, key)
        if exist_cnt == 2 and path != '' and not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(res)

    def onKeyRelease(self, evt, key):
        files = self.getFiles()
        for i in range(3):
            if i != key and not os.path.isfile(files[i]):
                self.ss[i].set('')
        res = getResult(files, key)
        self.tex1.delete(1.0, 'end')
        self.tex1.insert(1.0, res)
        return res

if __name__ == "__main__":
    top = myPanel()
    top.mainloop()
