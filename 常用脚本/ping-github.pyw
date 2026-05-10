import time
import threading
import tkinter
import urllib.request

title = '访问失败'

def update_status():
    while True:
        root.title(f'Github{title} - {time.strftime("%H:%M:%S")}')
        time.sleep(1)

def check_github():
    global title
    while True:
        t = time.time()
        try:
            response = urllib.request.urlopen('https://github.com', timeout=10)
            title = '访问成功'
        except urllib.error.URLError as e:
            title = '访问失败'
        except Exception as e:
            title = '访问异常'
        time.sleep(max(0, 10 - (time.time() - t)))


root = tkinter.Tk()
root.geometry('200x0')
root.attributes('-topmost', True)
root.attributes('-toolwindow', True)
root.resizable(False, False)

threading.Thread(target=check_github).start()
threading.Thread(target=update_status).start()

root.mainloop()
