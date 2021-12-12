"""
Usage:
    Drag `root` folder to this script.

File tree like:
    ~\root

    ~\root\ch1
    ~\root\ch2
    ~\root\ch3
    ...

    ~\root\ch1\001.jpg
    ~\root\ch1\002.jpg
    ~\root\ch1\003.jpg
    ...

    ~\root\ch2\001.jpg
    ~\root\ch2\002.jpg
    ~\root\ch2\003.jpg
    ...
"""

import os
import re
import sys
join = os.path.join

img  = lambda url: '<img src="%s" />' % url.replace('&', '&amp;')
href = lambda url, text: '<a href="%s.html">%s</a> ' % (url.replace('&', '&amp;'), text)
fns  = lambda s: [(s, int(n))for s, n in re.findall(r'(\D+)(\d+)', 'a%s0' % s)]


def save(file, lst):
    '''居中显示列表元素'''
    template = '<div id="top" style="text-align:center">\n%s\n</div>'
    with open(file + '.html', 'w') as f:
        f.write(template % '<br/>\n'.join(lst))


def MakeHtmls(root):
    folders = [n for n in os.listdir(root) if os.path.isdir(join(root, n))]
    folders = sorted(folders, key=fns)

    # 生成汇总Html
    data = [href('index', '目录')]
    for page, name in enumerate(folders):
        for file in os.listdir(join(root, name)):
            data.append(img(join(name, file)))
    save(join(root, 'all'), data)

    # 生成单文件夹汇总Html
    for page, name in enumerate(folders):
        header = href('index', '目录') \
              + (href(folders[page-1], '上一页') if page else '') \
              + (href(folders[page+1], '下一页') if page+1-len(folders) else '')
        data = [name, header]
        for file in os.listdir(join(root, name)):
            data.append(img(join(name, file)))
        data.append(header)
        save(join(root, name), data)
    save(join(root, 'index'), [href('all', '全部')] + [href(name, name) for name in folders])

    # 生成快捷跳转Html
    basename = os.path.basename(root)
    save(root, [href(join(basename, 'index'), basename)])


if len(sys.argv) > 1:
    for root in sys.argv[1:]:
        MakeHtmls(root)
else:
    MakeHtmls('美丽新世界')
