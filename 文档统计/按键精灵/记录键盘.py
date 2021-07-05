import time
from threading import Thread

import pynput
import pyautogui

LOG = time.strftime('RECORD_%Y%m%d_%H%M%S.log')

def pprint(*s):
    s1 = ' '.join(map(str, s)) + '\n'
    print(s1, end='')
    with open(LOG, 'a', encoding='u8') as f:
        s = f.write(s1)


class Monitor:
    def __init__(self):
        self.time = time.time()
        t1 = Thread(target=self.MouseListener)
        t2 = Thread(target=self.KeyboardListener)
        t1.start()
        t2.start()

    def on_move(self, x, y):
        return
        self.DelayPrint('pyautogui.moveTo(x=%d, y=%d)'%(x, y))

    def on_click(self, x, y, button, pressed):
        event = 'mouseDown' if pressed else 'mouseUp'
        self.DelayPrint("pyautogui.%s(x=%d, y=%d, button='%s')"%(event, x, y, button.name))

    def on_click_simple(self, x, y, button, pressed):
        if pressed:
            self.DelayPrint("pyautogui.click(x=%d, y=%d)"%(x, y))

    def on_scroll(self, x, y, dx, dy):
        self.DelayPrint('Scrolled {0}'.format((x, y)))

    def on_press(self, key):
        self.DelayPrint("pyautogui.keyDown(%s)"%key)

    def on_release(self, key):
        self.DelayPrint("pyautogui.keyUp(%s)"%key)

    def MouseListener(self):
        with pynput.mouse.Listener(on_move=self.on_move, on_click=self.on_click_simple, on_scroll=self.on_scroll) as self.mouse_listener:
            self.mouse_listener.join()

    def KeyboardListener(self):
        with pynput.keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as self.keyboard_listener:
            self.keyboard_listener.join()

    def Stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def Clock(self):
        t1 = time.time()
        pprint('time.sleep(%.3f)'%(t1 - self.time))
        self.time = t1

    def DelayPrint(self, s):
        self.Clock()
        pprint(s)


if __name__ == '__main__':
    m = Monitor()
    time.sleep(2)
    m.Stop()
