# -*- coding: utf-8 -*-
"""
屏幕区域截图与OCR文字识别工具

功能：捕获屏幕指定区域，进行OCR文字识别
依赖：opencv-python, numpy, pytesseract, pywin32
"""
import re

import cv2
import numpy as np
import pytesseract
import win32con
import win32gui
import win32ui


def grab_roi(left, top, w, h):
    """
    截取屏幕指定区域并转为 numpy 图像格式
    :param left:   区域左上角X坐标
    :param top:    区域左上角Y坐标
    :param w:      截取的宽度
    :param h:      截取的高度
    :return:     numpy.ndarray: RGB格式图像数组 (h, w, 3)
    """
    # 获取屏幕 DC
    hwin = win32gui.GetDesktopWindow()
    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()

    # 创建兼容位图
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, w, h)
    memdc.SelectObject(bmp)

    # 只拷需要的 ROI
    memdc.BitBlt((0, 0), (w, h), srcdc, (left, top), win32con.SRCCOPY)

    # 转 numpy
    signed_ints = bmp.GetBitmapBits(True)
    img = np.frombuffer(signed_ints, dtype=np.uint8)
    img = img.reshape((h, w, 4))  # B,G,R,A
    img = img[:, :, :3][:, :, ::-1]  # BGRA -> RGB

    # 清理
    win32gui.DeleteObject(bmp.GetHandle())
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    return img


def roi2text(roi_np, char_whitelist=None, pattern=None, psm=7, debug=False):
    """
    从截图中识别文字

    识别步骤：
    1. 灰度化
    2. Otsu 二值化
    3. Tesseract OCR（可配置字符白名单）
    4. 正则过滤（可配置匹配模式）
    5. 返回结果（若未匹配到则返回原始OCR结果或None）

    :param roi_np: numpy 数组格式的RGB图像
    :param char_whitelist: OCR字符白名单，如 "0123456789+-/"；None表示识别所有字符
    :param pattern: 正则表达式模式，用于过滤结果；None表示返回原始OCR结果
    :param psm: Tesseract页面分割模式（默认7=单行文本）
    :param debug: 是否打印调试信息
    :return: 识别到的字符串；若使用正则且未匹配到则返回None
    """
    # 1. 灰度化（输入为RGB格式图像）
    gray = cv2.cvtColor(roi_np, cv2.COLOR_RGB2GRAY)
    # 2. 二值化（背景深 -> 0，数字白 -> 255）
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 保存二值图用于调试
    # cv2.imwrite('binary.png', th)  # th 就是你刚才 Otsu 得到的二值图
    # cv2.imwrite('binary_inv.png', 255 - th)

    # 3. OCR识别
    config = f'--psm {psm}'
    if char_whitelist:
        config += f' -c tessedit_char_whitelist={char_whitelist}'
    txt = pytesseract.image_to_string(th, config=config)

    if debug:
        print("正则前的识别结果 =", txt)

    # 4. 正则过滤（若指定了pattern）
    if pattern:
        m = re.search(pattern, txt)
        return m.group(0) if m else None

    # 未指定pattern，返回原始OCR结果（去除首尾空白）
    return txt.strip() if txt.strip() else None


def main():
    """测试选择屏幕区域并执行OCR识别"""
    from screen_utils import get_screen_scaling
    from screen_selector import BoxSelector

    # 获取缩放
    scale_x, _ = get_screen_scaling()

    selector = BoxSelector()
    selector.run()
    # 获取按比例缩放后的结果
    result = selector.get_scaled_result(scale_x)
    print(f"按比例 {scale_x} 缩放后的选区结果：", result)

    roi = grab_roi(result.left, result.top, result.width, result.height)
    text = roi2text(roi)
    print("识别结果:", text)

    # 显示截图
    cv2.imshow('roi', roi)
    cv2.waitKey(0)
    # 保存截图用于调试
    # cv2.imwrite('roi.jpg', roi, [cv2.IMWRITE_JPEG_QUALITY, 95])


if __name__ == '__main__':
    main()
