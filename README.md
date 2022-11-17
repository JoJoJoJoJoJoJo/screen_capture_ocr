# 截图并自动识别文字的OCR工具

## OCR调用来自项目[chineseocr_lite](https://github.com/DayBreak-u/chineseocr_lite)

## 环境
- python3.7

- windows

## 使用方法
1. 克隆代码
```commandline
git clone https://github.com/JoJoJoJoJoJoJo/screen_capture_ocr.git
```

2. 设置截图快捷键(默认为ALT-SHIFT-P)

打开目录，编辑config.py `SCREEN_CAPTURE_KEY`

3. 安装依赖
```commandline
pip install -r requirements.txt
```

4. 启动
```commandline
python main.py
```

5. 使用快捷键截图并自动识别，识别结果上点击即可自动复制识别文字

## Demo
### 原始截图
<img src="https://github.com/JoJoJoJoJoJoJo/screen_capture_ocr/blob/main/demo/demo.png"/>

### 识别结果
<img src="https://github.com/JoJoJoJoJoJoJo/screen_capture_ocr/blob/main/demo/demo_result.png"/>

红色框体表示OCR区域，在上面点击即可显示识别结果（白底红字）并自动复制

（此处应有gif）

## 已知的问题
* 需要TK窗口获得焦点才能监听到快捷键

## TODO
- [ ] 最小化托盘运行， 快捷键唤醒
- [ ] linux / macos 系统支持
- [ ] 提高识别精度
- [ ] Release安装包
