# TODO: file_type默认全格式/输出排序/邮箱列表切换快速选择/全所邮箱/
# TODO: 邮箱带收件人名/排除列表可前台输入/错字容错/窗口大小适配

# 20190131 更新
# 打印已交人员名单
# 打印文件夹中所有文件情况
# 启动自动载入initialdir的检查结果
# 输入框实时更新检查结果
# 当不是地址时的报错

# 更新
# 下拉菜单
# 读取配置文件get_section函数
# 剥离配置保存到onClose函数

import os
import tkinter
import tkinter.filedialog
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

def get_section(ini_path, section):
    if not os.path.exists(ini_path):
        with open(ini_path, 'w') as f:
            pass
    ini = configparser.ConfigParser()
    ini.readfp(open(ini_path))
    result = []
    if not ini.has_section(section):
        ini.add_section(section)
    else:
        options = ini.options(section)
        for option in options:
            result.append([option, ini.get(section, option)])
    ini.write(open(ini_path,'w'))
    return result

def get_namelist(owners='', namelist=''):
    ss = namelist.split(';')
    names = {}
    for s in ss:
        if len(s) > 0:
            names[s.split('<')[0]] = s.split('<')[1][:-1]
    for owner in owners.split(','):
        if owner in names:
            names.pop(owner)
    return names

def count_lost_names(folder, namelist={}, owners=[], fullname=False):
    if os.path.isdir(folder):
        name_exist = {}
        name_not_exist = {}
        cnt_files = 0
        cnt_repeat = 0        
        if folder != '':
            files = os.listdir(folder)
            for file in files:
                file_type = file.split('.')[-1]
                types = get_config(config_path,'setting','file_type',default='xls,xlsx,doc,docx,ppt,pptx,txt').split(',')
                for t in types:
                    if file_type == t:
                        cnt_files += 1
                        for name in namelist.keys():
                            if name in file:
                                if name in name_exist:
                                    cnt_repeat += 1
                                name_exist[name] = file
            for name in namelist:
                if name not in name_exist:
                    name_not_exist[name] = namelist[name]
        yes = no = no_mail = ''
        for name in name_exist.keys():
            yes += name + '、'
        for name, mail in name_not_exist.items():
            no += name + '、'
            ##------------彩蛋------------##
            if fullname: #ini.has_section('fullname')
                no_mail += '%s<%s>,'%(name,mail)
            else:
                no_mail += mail + ','
            ##------------彩蛋------------##
        template = get_config(config_path,'setting','template',
                              default='共有文件%%s个：符合文件格式%%s个，不含姓名%%s个，重复姓名%%s个。\n已交文档%%s人：%%s\n未交文档%%s人：%%s\n群发邮件地址：')
        message = template%(len(files),cnt_files,cnt_files-cnt_repeat-len(name_exist),cnt_repeat,len(name_exist),yes[:-1],len(name_not_exist),no[:-1])
    else:
        message = '找不到指定的路径。'
        no_mail = ''
    return message, no_mail

def test(a):
    print(a)

def setCenter(top):
    top.update_idletasks()
    x = (top.winfo_screenwidth()  - top.winfo_reqwidth())/2
    y = (top.winfo_screenheight() - top.winfo_reqheight())/2
    top.geometry('+%d+%d'%(x,y))

class myPanel(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self, 'lsx')

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        
        self.file1 = tkinter.StringVar()
        
        self.tex1 = tkinter.Text(self, height=8)
        self.tex2 = tkinter.Text(self, height=10)
        ent1      = tkinter.Entry(self, textvariable=self.file1, width=1)
        btn1      = tkinter.Button(self, text='选择', command=self.selectPath)
        btn2      = tkinter.Menubutton(self, text='分组',relief=tkinter.RAISED)
        self.menu = tkinter.Menu(btn2, tearoff=False)

        owners    = get_config(config_path, 'namelist', 'owners')
        self.group = get_config(config_path, 'setting', 'savegroup')
        groups    = get_section(config_path, 'groups')
        self.namelist = {}
        for group, namelist_s in groups:
            namelist = get_namelist(namelist=namelist_s)
            self.addMenu(group, (group, namelist))
            if group == self.group:
                self.namelist = namelist
        self.menu.add_separator()
        self.menu.add_command(label='编辑分组', command=self.editMenu)
        
        btn2.config(menu=self.menu)

        self.tex1.grid(row=2, column=0, padx=2, pady=2, columnspan=99, sticky=tkinter.NSEW)
        self.tex2.grid(row=4, column=0, padx=2, pady=2, columnspan=99, sticky=tkinter.NSEW)
        ent1     .grid(row=0, column=0, padx=2, pady=2, columnspan=97, sticky=tkinter.EW)
        btn1     .grid(row=0, column=97, padx=2, pady=2)
        btn2     .grid(row=0, column=98, padx=2, pady=2)

        initialdir = get_config(config_path,'setting','savepath')
        self.file1.set(initialdir)
        self.selectPath(open_dir=False)

        ent1.bind('<KeyRelease>', self.onKeyRelease)
        ent1.bind('<Destroy>', self.onClose)

        setCenter(self)

    def onClose(self, evt):
        # print('onClose')
        get_config(config_path,'setting','savepath',default=self.path,overwrite=True)
        get_config(config_path,'setting','savegroup',default=self.group,overwrite=True)

    def editMenu(self):
        os.popen(config_path)

    def addMenu(self, group, data):
        group, namelist = data
        self.menu.add_radiobutton(label=group, command=lambda:self.selectMenu(group, namelist))

    def selectMenu(self, group, namelist):
        self.group = group
        self.namelist = namelist
        self.selectPath(open_dir=False)

    def selectPath(self, open_dir=True):
        print(self.namelist)
        initialdir = self.file1.get()
        if open_dir:
            path = tkinter.filedialog.askdirectory(initialdir=initialdir)
            if path != '':
                self.file1.set(path)
        self.path = self.file1.get()
        owners = get_config(config_path,'namelist','owners')
        yes, no = count_lost_names(self.path, namelist=self.namelist, owners=owners)
        self.tex1.delete(1.0, 'end')
        self.tex1.insert(1.0, yes)
        self.tex2.delete(1.0, 'end')
        self.tex2.insert(1.0, no)

    def onKeyRelease(self, evt):
        # print(evt.keysym)
        self.selectPath(open_dir=False)

if __name__ == "__main__":
    config_path = 'config.ini'
    top = myPanel()
    top.mainloop()
