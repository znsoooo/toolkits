# Author: 硫酸锌01(znsoooo)
# Github: github.com/znsoooo
# Mail  : 11313213@qq.com

# build
# 20200406

# TIPS
# 折叠节点不受影响

# TODO
# 当text中出现xml中无法识别的符号时(比如"<>,等)
# mainidea有无可能id不是101
# parentid和id位置有时会对调
# 多个主节点时
# 批注无法体现(topictype参数)


import re


def ReadHtml(html):
    with open(html, encoding='u8') as f:
        s = f.read()

    s = s.replace(' id="101"', ' ed:parentid="100" id="101"') # ed:topictype="mainidea"
    gs = re.findall(r'(<g.*?id=".*?".*?id=".*?".*?>)[\s\S]*?<text.*?>([\s\S]*?)</text>[\s\S]*?</g>', s)
    texts = []
    for g in gs:
        id = int(re.findall(r' id="(.*?)"', g[0])[0])
        parentid = int(re.findall(r' ed:parentid="(.*?)"', g[0])[0])
        text = ''.join(re.findall(r'<tspan.*?>(.*?)</tspan>', g[1])).replace('"', ' ') # text 去掉引号
        texts.append([id, parentid, text])

    return texts


def GetMainId(texts, id=101):
    for id2, parentid, text in texts:
        if id2 == id:
            return id, text


def GetChildren(texts, parentid):
    res = []
    for id, parentid2, text in texts:
        if parentid2 == parentid:
            res.append([id, text])
    return res


def Decorate(texts, parentid, text): # iterate spaces
    res = []
    children = GetChildren(texts, parentid)
    res = ['<outline text="%s">'%text]
    for id, text2 in children:
        res += ['    ' + line for line in Decorate(texts, id, text2)]
    res += ['</outline>']
    return res


def Decorate2(texts, parentid, text, level): # calculate spaces
    res = []
    children = GetChildren(texts, parentid)
    res = ['    ' * level + '<outline text="%s">'%text]
    for id, text2 in children:
        res += Decorate2(texts, id, text2, level+1)
    res += ['    ' * level + '</outline>']
    return res


def HtmlToOpml(open_html, save_opml, add_main=None): # 没有add_main会导致脑图如花状从中间向四周散开, 但是实际上也可以设置主节点的结构样式来改变
    texts = ReadHtml(open_html)
    if add_main:
        id, text = 100, add_main
    else:
        id, text = GetMainId(texts)

    with open(save_opml, 'w', encoding='u8') as f:
        f.write('<opml version="1.0">\n    <body>\n'
                + '\n'.join(Decorate2(texts, id, text, 2))
                + '\n    </body>\n</opml>')



# HtmlToOpml('主案设计.html', '主案设计.opml', add_main='Main')
HtmlToOpml('主案设计2.html', '主案设计.opml')


