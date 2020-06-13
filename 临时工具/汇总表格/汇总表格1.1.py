# TODO: listdir排除文件夹/无后缀名文件/昵称姓名

# 20190211更新
# 文件名重复自动生成编号
# 跳过含有'~$'的临时文件
# 文件重命名失败的异常处理并计数
# 文件重命名情况简报弹窗
# 正则表达式规则重命名模板(原为字符串格式化输出)
# 匹配6位数字日期

import os
import re
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import configparser

def get_config(ini_path, section, option, default='', overwrite=False):
    if not os.path.exists(ini_path):
        with open(ini_path, 'w') as f:
            pass
    ini = configparser.ConfigParser()
    ini.readfp(open(ini_path))
    if not ini.has_section(section):
        ini.add_section(section)
    if (not ini.has_option(section, option)) or overwrite:
        ini.set(section, option, default)
    result = ini.get(section, option)
    ini.write(open(ini_path,'w'))
    return result

def get_namelist(path, owner_default='', namelist_default=''):
    namelist = get_config(path,'namelist','namelist',default=namelist_default)
    ss = namelist.split(';')
    names = {}
    for s in ss:
        if len(s) > 0:
            names[s.split('<')[0]] = s.split('<')[1][:-1]
    return names

def find_name(string, namelist):
    string = string.replace(' ','').replace('　','')
    name = ''
    for n in namelist:
        if n in string:
            name = n
    return name

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))


class RecheckBox(tkinter.Toplevel):
    def __init__(self, parent, folder, rename_files):
        tkinter.Toplevel.__init__(self, parent)

        self.rename_files = rename_files
        self.folder = folder
        self.delete_item = []
        
        self.geometry('800x540')
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        tree = tkinter.ttk.Treeview(self, show='headings')
        tree['columns']=('编号','类型','文件名','重命名')
        tree.column('编号',width=10,anchor='center')
        tree.column('类型',width=10,anchor='center')
        tree.column('文件名',width=300)
        tree.column('重命名',width=300)
        tree.heading('编号',text='编号')
        tree.heading('类型',text='类型')
        tree.heading('文件名',text='文件名')
        tree.heading('重命名',text='重命名')

        for i, file in enumerate(rename_files):
            tree.insert('',i,text=i,values=(i+1,file[0].split('.')[-1],file[0],file[1]))

        bt0 = tkinter.Button(self,text='撤销',command=self.onCancel)
        bt1 = tkinter.Button(self,text='确定',command=self.onOK)
        bt2 = tkinter.Button(self,text='取消',command=self.onClose)
        tree.grid(row=0,column=0,columnspan=4,sticky=tkinter.NSEW)
        bt0.grid(row=1, column=1, padx=2, pady=2)
        bt1.grid(row=1, column=2, padx=2, pady=2)
        bt2.grid(row=1, column=3, padx=2, pady=2)
        
        tree.bind('<Double-1>', self.setVisible)
        self.tree = tree
        setCenter(self)

    def onCancel(self):
        item = self.delete_item.pop()
        row = int(item[0])-1
        self.tree.insert('',row,text=row,values=(item[0],item[1],item[2],item[3]))
        self.rename_files[row] = [item[2],item[3]]

    def onClose(self):
        self.destroy()

    def onOK(self):
        cnt_ok = 0
        cnt_fail = 0
        cnt_exist = 0
        for file_name, file_name_new in self.rename_files:
            if file_name_new != '':
                try:
                    os.rename(self.folder+'/'+file_name, self.folder+'/'+file_name_new)
                    cnt_ok += 1
                except FileExistsError:
                    repeat_cnt = 0
                    while 1:
                        try:
                            repeat_cnt += 1
                            os.rename(self.folder+'/'+file_name, self.folder+'/'+str(repeat_cnt)+'-'+file_name_new)
                            break
                        except:
                            pass
                    cnt_exist += 1
                except PermissionError:
                    cnt_fail += 1
                    print('PermissionError: 另一个程序正在使用此文件，进程无法访问。')
                except Exception as e:
                    cnt_fail += 1
                    print('Exception:', e)
        self.destroy()
        tkinter.messagebox.showinfo(message='已重命名%s个文件，重复文件%s个，重命名失败%s个。'%(cnt_ok,cnt_exist,cnt_fail))

    def setVisible(self, evt):
        # column = int(self.tree.identify_column(evt.x)[1:],16)-1
        # row = int(self.tree.identify_row(evt.y)[1:],16)-1
        # print(column, row)
        # 
        # for i in range(4):
        #     self.tree.set(self.tree.selection(),column=i,value='')
        
        item = self.tree.selection()
        if item != '':
            item_text = self.tree.item(self.tree.selection(), 'values')
            self.tree.delete(self.tree.selection())
            row = int(item_text[0])-1
            self.rename_files[row] = ['','']
            self.delete_item.append(item_text)

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.ent1_tex = tkinter.StringVar()
        self.ent2_tex = tkinter.StringVar()
        ent1 = tkinter.Entry(self, width=60, textvariable=self.ent1_tex)
        btn1 = tkinter.Button(self, text='文件夹', command=self.selectPath)
        ent2 = tkinter.Entry(self, textvariable=self.ent2_tex)
        btn2 = tkinter.Button(self, text='重命名', command=self.renameFiles)
        ent1.grid(row=0, column=0,  padx=2, pady=2, sticky=tkinter.EW)
        btn1.grid(row=0, column=98, padx=2, pady=2)
        ent2.grid(row=1, column=0,  padx=2, pady=2, sticky=tkinter.EW)
        btn2.grid(row=1, column=98, padx=2, pady=2)

        initialdir = get_config(config_path,'setting','savepath')
        initialtemplate = get_config(config_path,'setting','template')
        self.ent1_tex.set(initialdir)
        self.ent2_tex.set(initialtemplate)
        
        setCenter(self)

    def selectPath(self):
        initialdir = self.ent1_tex.get()
        path = tkinter.filedialog.askdirectory(initialdir=initialdir)
        if path != '':
            self.ent1_tex.set(path)
            get_config(config_path,'setting','savepath',default=path,overwrite=True)
            if self.ent1_tex.get() != '':
                self.renameFiles()

    def renameFiles(self):
        folder = self.ent1_tex.get()
        files1 = os.listdir(folder)
        files = []
        for file in files1:
            if '~$' not in file:
                files.append(file)
        rename_files = []
        namelist = get_namelist(config_path)
        template = self.ent2_tex.get()
        if template != '':
            get_config(config_path,'setting','template',default=template.replace('%','%%'),overwrite=True)
        for file_name in files:
            name = name2 = find_name(file_name, namelist)
            if len(name) == 2:
                name2 = name + '__'

            date = re.findall(r'\d\d\d\d\d\d\d\d',file_name)
            if len(date) > 0:
                date = date[0]
            else:
                date = re.findall(r'\d\d\d\d\d\d',file_name)
                if len(date) > 0:
                    date = '20' + date[0]
                else:
                    date = '00000000'

            file_type = file_name.split('.')[-1]
            # file_name_new = (template+'.%s')%(name,date,file_type)
            template = template.replace('\\name2','\\2').replace('\\name','\\1').replace('\\date','\\3')
            file_name_new = re.sub(r'(.*) (.*) (.*)', template, (name+' '+name2+' '+date))+'.'+file_type
            if name == '':
                file_name_new = ''
            rename_files.append([file_name,file_name_new])

        a = RecheckBox(self, folder, rename_files)


if __name__ == "__main__":
    config_path = 'config.ini'
    top = myPanel()
    top.mainloop()
