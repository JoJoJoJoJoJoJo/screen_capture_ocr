import tkinter
import tkinter.filedialog
import os
import win32con
import win32clipboard
import ctypes
from PIL import ImageGrab, ImageTk
from time import sleep
from tkinter import StringVar
from model import OcrHandle
from config import SCREEN_CAPTURE_KEY

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)  # 获取屏幕缩放


class MainUI(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(*args, **kwargs)
        self.geometry('200x180+400+300')
        self.resizable(False, False)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.capture_ui = None
        self.tk.call('tk', 'scaling', ScaleFactor / 75)  # 适应屏幕缩放

        def get_screen_capture(event):
            filename = 'tmp.png'
            im = ImageGrab.grab()
            im = im.resize((screen_width, screen_height))
            im.save(filename)
            im.close()
            self.capture_ui = ScreenCapture(self, filename)

        self.bind('<{}>'.format(SCREEN_CAPTURE_KEY), get_screen_capture)


class ScreenCapture:
    def __init__(self, main, png):
        self.root = main
        screen_width = main.screen_width
        screen_height = main.screen_height
        self.x = tkinter.IntVar(value=0)
        self.y = tkinter.IntVar(value=0)
        self.selectPosition = None
        self.sel = False
        self.filename = png
        self.captured = None

        self.top = tkinter.Toplevel(self.root, width=screen_width, height=screen_height)
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screen_width, height=screen_height)
        self.p_w_picpath = tkinter.PhotoImage(file=png)
        self.canvas.create_image(0, 0, anchor=tkinter.NW, image=self.p_w_picpath)

        def onLeftButtonDown(event):
            self.x.set(event.x)
            self.y.set(event.y)
            self.sel = True
        self.canvas.bind('<Button-1>', onLeftButtonDown)

        def onLeftButtonMove(event):
            if not self.sel:
                return
            global lastDraw
            try:
                self.canvas.delete(lastDraw)
            except:
                pass
            lastDraw = self.canvas.create_rectangle(self.x.get(), self.y.get(), event.x, event.y, outline='green')
        self.canvas.bind('<Motion>', onLeftButtonMove)

        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except:
                pass
            sleep(0.1)
            left, right = sorted([self.x.get(), event.x])
            top, bottom = sorted([self.y.get(), event.y])
            self.selectPosition = [left, top, right, bottom]
            self.top.destroy()
            text = StringVar()
            text.set('old')
            text.set('选择的区域：\n{}'.format(str(self.selectPosition)))
            self.root.state('normal')
            os.remove(self.filename)
            im = ImageGrab.grab(bbox=self.selectPosition)
            # for debug
            label = tkinter.Label(self.root, textvariable=text)
            label.place(x=10, y=30, width=160, height=120)

            selected_width = self.selectPosition[2] - self.selectPosition[0]
            selected_height = self.selectPosition[3] - self.selectPosition[1]
            top_new = tkinter.Toplevel(self.root)
            top_new.geometry(
                '{}x{}+{}+{}'.format(selected_width, selected_height, self.selectPosition[0], self.selectPosition[1]))
            top_new.resizable(False, False)
            canvas_new = OCRCanvas(im, top_new, bg='white', width=selected_width, height=selected_height)
            self.captured = ImageTk.PhotoImage(im)
            canvas_new.create_image(0, 0, anchor=tkinter.NW, image=self.captured)
            canvas_new.show_ocr_area()
            canvas_new.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)

        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)


class OCRCanvas(tkinter.Canvas):
    def __init__(self, image, *args, **kwargs):
        super(OCRCanvas, self).__init__(*args, **kwargs)
        self.data = self.ocr(image)

        def mouseover(event):
            if self.is_in_area(event.x, event.y):
                self.config(cursor="hand2")
            else:
                self.config(cursor="arrow")

        def click_ocr_area(event):
            _data = self.get_area_data(event.x, event.y)
            if _data:
                self.show_ocr_text(_data)
                self.pack()

        self.bind('<Motion>', mouseover)
        self.bind('<ButtonRelease-1>', click_ocr_area)

    def show_ocr_area(self):
        for _data in self.data:
            self.create_rectangle(_data['area'], outline='red')

    def show_ocr_text(self, data_line):
        if data_line['clicked']:
            self.set_clipboard(data_line['text'])
            return
        area = data_line['area']
        text = data_line['text']
        self.create_rectangle(area, outline='red', fill='white')
        self.create_text(area[0], area[1], anchor=tkinter.NW, text=text, fill='red')
        self.set_clipboard(data_line['text'])
        data_line['clicked'] = True

    def ocr(self, image):
        handler = OcrHandle()
        short_size = 960
        res = handler.text_predict(image, short_size)
        result = []
        for line in res:
            pos, text, accurate = line
            area = [pos[0][0], pos[0][1], pos[2][0], pos[2][1]]  # 左上 右下
            result.append({'area': area, 'text': text, 'clicked': False})
        return result

    def is_in_area(self, x, y):
        for _data in self.data:
            area = _data['area']
            if area[0] <= x <= area[2] and area[1] <= y <= area[3]:
                return True
        return False

    def get_area_data(self, x, y):
        for _data in self.data:
            area = _data['area']
            if area[0] <= x <= area[2] and area[1] <= y <= area[3]:
                return _data

    def set_clipboard(self, text):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    ui = MainUI()
    ui.title('Screen Capture OCR')
    ui.mainloop()
