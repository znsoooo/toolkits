# 20200319 build
# 20200608 fix
# 20201022 匹配嵌套函数

import re
import os


# 读取剪切板
##import tkinter
##app = tkinter.Tk()
##s = app.clipboard_get()
##app.destroy()


def ReadAllFiles(folder, exts):
    ss = ''
    for path, folders, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in exts:
                with open(os.path.join(path, file), 'rb') as f:
                    sb = f.read()
                try:
                    ss += sb.decode() + '\n'
                except:
                    ss += sb.decode('gbk', errors='ignore') + '\n'
    return ss


def RemoveComment(s):
    # 去除注释
    s = re.sub(r'//.*', '', s)
    s = re.sub(r'/\*[\s\S]*?\*/', '', s)
    s = re.sub(r'#include .*', '', s)
    s = re.sub(r'#define .*', '', s)
    return s


def ExtractBlocks(s):
    # 取出区块
    blocks = []
    cnt = 0
    block = ''
    for c in s:
        block += c
        if c == '{':
            cnt += 1
        if c == '}':
            cnt -= 1
            if cnt == 0:
                blocks.append(block)
                block = ''
    return blocks


def ExtractFunctions(s):
    s = re.sub(r'\s+', ' ', s)
    n = s.find('{')
    funs1 = re.findall(r'(\w+)\s*(\(.*?\))', s[:n])
    funs2 = re.findall(r'(\w+)\s*\(', s[n:])
    funs3 = list(set(funs2))    # 去重
    funs3.sort(key=funs2.index) # 排序

    if len(funs1) == 0: # 如typedef struct不是函数
        return

    name, param = funs1[-1] # 最外层大括号前的最后一个函数

    if name in funs3:
        funs3.remove(name) # 防止递归

    return name, param, funs3


def Unfold(functions_all, name, level):
    lines = []
    if name in functions_all:
        param, inner = functions_all[name]
        # print(' |   ' * level)
        # print(('    |' * level + ' - ')[3:] + name + param)
        lines.append(' |   ' * level)
        lines.append(('    |' * level + ' - ')[3:] + name + param)
        for name2 in inner:
            if name2 in functions_all:
                # print('--' * level + '--', name2)
                lines += Unfold(functions_all, name2, level+1)
    return lines


def AnalysisCode(folder, exts, save_file=None):
    s = ReadAllFiles(folder, exts)
    s = RemoveComment(s)
    blocks = ExtractBlocks(s)

    functions_all = {}
    for block in blocks:
        functions = ExtractFunctions(block)
        if functions: # block不是函数结构时functions=None
            name, param, inner = functions
            # print('%4d行:'%block.count('\n'), name)
            functions_all[name] = [param, inner]

    lines = Unfold(functions_all, 'main', 0)
    tree = '\n'.join(lines)

    if save_file:
        with open(save_file, 'w') as f:
            f.write(tree)

    return tree



folder = r'E:\cpp\hello'
AnalysisCode(folder, ['.cpp'], '分析_原版_fix.txt')
