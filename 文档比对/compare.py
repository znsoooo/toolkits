import difflib

def readFile(filename):
    with open(filename,'r', encoding='utf-8') as f:
        return f.read()
        
def makeDiff(old, new):
    res = []
    rows = 0
    for s in difflib.ndiff(old.splitlines(), new.splitlines()):
        if s[0] is ' ':
            rows += 1
        elif s[0] in ['+', '-']:
            if rows != 0:
                res += [str(rows)]
                rows = 0
            res += [s]
    res += [str(rows)]
    return '\n'.join(res)

def removeDiff(old, diff, reverse=False):
    res = []
    arrow = 0
    old = old.splitlines()
    if reverse:
        a, b = '-', '+'
    else:
        a, b = '+', '-'
    for s in diff.splitlines():
        if s[0] == a:
            res += [s[2:]]
        elif s[0] == b:
            arrow += 1
        else:
            try:
                rows = int(s)
                res += old[arrow:arrow+rows]
                arrow += rows
            except:
                pass
    return '\n'.join(res)

def makeDiffFile(old, new, diff):
    t1 = readFile(old)
    t2 = readFile(new)
    t3 = makeDiff(t1, t2)
    with open(diff, 'w') as f:
        f.write(t3)
    return t3

def removeDiffFile(old, new, diff, reverse=False):
    if reverse:
        new, old = old, new
    t1 = readFile(old)
    t3 = readFile(diff)
    t2 = removeDiff(t1, t3)
    with open(new, 'w') as f:
        f.write(t2)
    return t2

if __name__ == '__main__':
    t1 = readFile('old.py')
    t2 = readFile('new.py')
    t3 = makeDiff(t1, t2)
    print(t3)

    t4 = removeDiff(t1, t3, False)
    print(t4)

    print(makeDiffFile  ('old.py', 'new.py',      'diff.txt'))
    print(removeDiffFile('old.py', 'generate.py', 'diff.txt'))

    makeDiffFile  (r'E:\z\Python27\所网通讯录\history\所网通讯录v1.02文件夹通讯录、多线程比较.py', r'E:\z\Python27\所网通讯录\所网通讯录v1.04_MD5校验.py', 'diff.txt')
