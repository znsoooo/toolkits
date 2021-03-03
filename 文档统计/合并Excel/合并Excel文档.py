# build 20210225
# 多选选择xls/xlsx格式的文件并按照"路径/文件名/工作表名/表内容"合并保存为1个xls文件

# TODO
# 读取进度条
# 合并csv文件
# 合并word和ppt

import os
import wx
import xlrd
import xlwt


def UniqueFile(file): # Good!
    root, ext = os.path.splitext(file)
    cnt = 1
    while os.path.exists(file):
        file = '%s_%d%s'%(root, cnt, ext)
        cnt += 1
    return file


def ReadExcel(file):
    xls = xlrd.open_workbook(file)
    data = []
    for sheet in xls.sheets():
        sheet_name = sheet.name
        for row in range(sheet.nrows):
            rows = [sheet_name] + sheet.row_values(row)
            for c, cell in enumerate(rows):
                if isinstance(cell, float):
                    if cell.is_integer():
                        rows[c] = str(int(cell))
                    else:
                        rows[c] = str(cell)
            data.append(rows)
    return data


def ReadExcels(files):
    data = []
    success = []
    errors  = []
    for file in files:
        path, filename = os.path.split(file)
        try:
            data += [[path, filename] + row for row in ReadExcel(file)]
            success.append(file)
        except:
            errors.append(file)

    MessageAlert(success, errors)

    return data


def MessageAlert(success, errors):
    msg1 = '成功%d/%d个文件，失败%d个文件。'%(len(success)-len(errors), len(success), len(errors))
    msg2 = msg1 + '\n\n成功：\n' + '\n'.join(success) + '\n\n失败：\n' + '\n'.join(errors) + '\n'
    wx.MessageBox(msg1 + '保存日志到log.txt。', '结果')
    with open('log.txt', 'w', encoding='u8') as f:
        f.write(msg2)


def WriteXls(data, file):
    xls = xlwt.Workbook('u8')
    sheet = xls.add_sheet('sheet1', True)
    for r, row in enumerate(data):
        for c, cell in enumerate(row):
            sheet.write(r, c, cell)
    xls.save(file)


# unuse
def MyWalk(path, exts=[]):
    result = []
    for root, folders, files in os.walk(path):
        result += [os.path.join(root, file) for file in files if os.path.splitext(file)[1] in exts]
    return result


# unuse
def ExtractDate(s):
    res = re.findall('(\d\d\d\d)\D?(\d\d)\D?(\d\d)', s)
    if res:
        return ''.join(res[0])
    res = re.findall('(\d\d)\D?(\d\d)\D?(\d\d)', s)
    if res:
        return '20' + ''.join(res[0])
    return ''


if __name__ == '__main__':
    # data = ReadExcels(MyWalk('2020', ['.xls', '.xlsx']))
    # WriteExcel(data, '20202汇总.xls')

    import time

    app = wx.App()
    dlg = wx.FileDialog(None, wildcard = 'Excel文档 (*.xls,*.xlsx)|*.xls;*.xlsx',
                        style = wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()
        data = ReadExcels(files)
        savefile = UniqueFile('汇总_%d个文档_%s.xls'%(len(files), time.strftime('%Y%m%d')))
        dlg = wx.FileDialog(None, wildcard = 'Excel文档 (*.xls)|*.xls',
                            defaultDir = os.getcwd(), # 用'.'在打包之后无法保持目录不变
                            defaultFile = savefile,
                            style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            WriteXls(data, path)

        import subprocess
        subprocess.Popen('notepad log.txt') # 用os.popen在打包之后无法打开

    app.MainLoop()

