# py-screen-ocr

一个轻量级的 Windows 屏幕 OCR 工具。通过鼠标框选屏幕区域，使用 Tesseract OCR 持续识别区域内的文字。
支持配置字符白名单、正则匹配模式和页面分割模式（PSM）。
本项目为学习练手 demo，涉及 Tkinter GUI 开发、OpenCV 图像处理和 Win32 API 屏幕截图等技术。

## 技术栈

- **Python 3** - 主要开发语言
- **Tkinter** - GUI 界面开发
- **OpenCV** - 图像处理（灰度化、二值化）
- **Tesseract OCR** - 光学字符识别引擎
- **pywin32** - Windows API 调用、屏幕截图
- **多线程编程** - 后台 OCR 识别循环
- **DPI 缩放处理** - 适配高分辨率屏幕

## 依赖安装

### 1. 安装 Tesseract OCR（必需）

下载并安装 Tesseract OCR：https://github.com/UB-Mannheim/tesseract/wiki

安装完成后，确保 `tesseract.exe` 在系统 PATH 中，或在代码中指定路径。

## 使用方法

### 方式一：直接下载（推荐）

从 [Releases](../../releases) 页面下载最新的 `screen-ocr.exe`，双击运行即可。

### 方式二：从源码运行

#### 环境要求

- **Python**: 3.11（开发及测试环境，其他版本暂未验证）

```bash
# 克隆代码仓库
git clone --depth 1 https://github.com/soladuor/py-screen-ocr.git
cd py-screen-ocr

# 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate
#pip install opencv-python numpy pytesseract pywin32
pip install -r requirements.txt

# 运行主程序
python src/main.py
```

### 操作说明

1. 点击 **设置框选** 按钮，在屏幕上拖动鼠标选择要识别的区域

2. （可选）配置 OCR 参数：
    - **字符白名单**：限制 OCR 只识别特定字符，如 `0123456789`
    - **匹配模式**：使用正则表达式过滤结果，如 `\d+`
    - **识别模式**：选择适合内容的页面分割模式

3. 点击 **开始** 按钮，程序将每秒对选定区域进行 OCR 识别

4. 使用 **显示区域** 按钮可以在屏幕上显示当前选区的红色边框

## 可配置项

| 配置项   | 说明                         | 示例/选项                   |
|-------|----------------------------|-------------------------|
| 字符白名单 | OCR 只识别这些字符，留空识别所有字符       | `0123456789`            |
| 匹配模式  | 正则表达式，用于过滤 OCR 结果，留空返回全部结果 | `\d+`                   |
| 识别模式  | Tesseract 页面分割模式           | 单行文本、单个单词、单个字符、文本块、自动分割 |

## 文件说明

```
py-screen-ocr/
├── src/                    # 源代码
│   ├── main.py             # 主程序入口，GUI 界面
│   ├── screen_ocr.py       # 屏幕截图和 OCR 识别
│   ├── screen_selector.py  # 屏幕区域选择工具
│   └── screen_utils.py     # 屏幕工具函数（分辨率获取、DPI 缩放等）
├── docs/                   # 文档
│   ├── BUILD.md            # 打包指南（GitHub Actions）
│   ├── BUILD_LOCAL.md      # 本地打包指南
│   └── RELEASE_NOTES.md
├── README.md
├── LICENSE
└── requirements.txt
```

## 注意事项

- 本工具仅支持 Windows 系统
- 需要安装 Tesseract OCR 引擎
- 高 DPI 显示器已自动处理缩放问题

## 免责声明

本项目仅供学习和技术研究使用。作者不对因使用或滥用本工具所产生的任何后果承担责任。使用者应自行确保其使用方式符合相关法律法规及所涉及软件或内容的使用条款。使用本工具即表示您同意自行承担一切风险。
