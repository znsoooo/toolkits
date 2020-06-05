# 说明
- 程序展现了一个用pyinstaller工具可以打包成cmd应用的程序样例
- 运行"打包exe.bat"可自动完成打包
- 程序通过API访问云表完成自动任务，但是appKey已经移除，以及需要相应环境，所以程序无法直接运行

## feature
- 自动获取本机用户名
- 本地存储用户自定义信息
- 确认提交信息并允许更改
- input确认信息是否正确 -- [y/n]确认
- 默认不更改和输入新值修改的写法 -- new = input(hint) or origin
- 多电脑拷贝自动辨认主机发生变化(通过获取本机MAC地址)

## debug打包
- 避免pyinstaller打包成debug模式时产生报错
- 避免debug运行时程序运行结束自动退出(Press Enter to finish)
- pprint设置延时和空行增加程序调试运行时的段落感
