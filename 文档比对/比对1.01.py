import tkinter
import tkinter.filedialog

import os
import re
import difflib
import zipfile
from win32com import client

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

def selectPath(text, paths, n):
    initialdir = '/'.join(paths[n].get().split('/')[:-1])
    path = tkinter.filedialog.askopenfilename(initialdir=initialdir)
    if path != '':
        paths[n].set(path)
    path1 = paths[0].get()
    path2 = paths[1].get()
    s1 = file2text(path1)
    s2 = file2text(path2)
    ss1 = s1.splitlines()
    ss2 = s2.splitlines()
    d = difflib.Differ()
    diff = d.compare(ss1, ss2)
    FULL_TEXT = True
    if not FULL_TEXT:
        result = '\n'.join(list(diff))
    else:
        result = ''
        for i, line in enumerate(list(diff)):
            if line[:2] != '  ':
                result += '%4d '%i + line +'\n'
    text.delete(1.0, 'end')
    text.insert(1.0, result)

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

def main():
    top = tkinter.Tk()
    top.columnconfigure(0,weight=1)
    top.rowconfigure(0,weight=1)
    file1 = tkinter.StringVar()
    file2 = tkinter.StringVar()
    tex1 = tkinter.Text(top)
    ent1 = tkinter.Entry(top, textvariable=file1, width = 1)
    ent2 = tkinter.Entry(top, textvariable=file2, width = 1)
    btn1 = tkinter.Button(top, text='文件1', command=lambda:selectPath(tex1,(file1,file2),0))
    btn2 = tkinter.Button(top, text='文件2', command=lambda:selectPath(tex1,(file1,file2),1))
    tex1.grid(row=0, column=0,  padx=2, pady=2, columnspan=99, sticky=tkinter.NSEW)
    ent1.grid(row=1, column=0,  padx=2, pady=2, columnspan=97,  sticky=tkinter.EW)
    ent2.grid(row=2, column=0,  padx=2, pady=2, columnspan=97,  sticky=tkinter.EW)
    btn1.grid(row=1, column=98, padx=2, pady=2)
    btn2.grid(row=2, column=98, padx=2, pady=2)
    setCenter(top)
    top.mainloop()

if __name__ == "__main__":
    main()
