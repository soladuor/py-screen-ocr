# -*- coding: utf-8 -*-
"""
屏幕分辨率与DPI工具
获取屏幕的逻辑分辨率、真实分辨率、缩放比例和DPI信息
"""
import ctypes.wintypes
import math
from tkinter import Tk

import win32con
import win32gui
import win32print


def get_logical_resolution():
    """获取缩放后的分辨率"""
    user32 = ctypes.windll.user32
    scaling_width = user32.GetSystemMetrics(0)
    scaling_height = user32.GetSystemMetrics(1)
    return scaling_width, scaling_height


def get_real_resolution():
    """
    获取真实分辨率
    通过 GDI 获取真实分辨率，避免 DPI 缩放影响
    """

    # 获取屏幕DC
    hDC = win32gui.GetDC(0)

    real_width = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    real_height = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)

    # 释放DC
    win32gui.ReleaseDC(0, hDC)

    return real_width, real_height


def get_screen_scaling(precision=2):
    """
    计算屏幕缩放比例
    通过真实分辨率 / 逻辑分辨率 计算缩放比例
    :param precision: 小数精度, 默认保留2位
    :return: 缩放比例 (scale_x, scale_y)
    """
    real_width, real_height = get_real_resolution()
    logical_width, logical_height = get_logical_resolution()

    scale_x = real_width / logical_width
    scale_y = real_height / logical_height

    # print(f"屏幕缩放比例: X={scale_x:.2f}, Y={scale_y:.2f}")

    # 保留小数
    return round(scale_x, precision), round(scale_y, precision)


"""
GDI 设计于 1990 年代，当时没有高 DPI 显示器，所有显示器的 DPI 都是 96
因此 GDI 坐标系中，1 英寸 = 96 像素（逻辑像素）
            ↓
实际渲染时：Windows 根据系统缩放，把 96 虚拟像素 
            映射到 144/192 等物理像素
            （即不同缩放比例下，1 英寸对应的物理像素数不同）

而实际上的物理像素密度（DPI）可以通过 屏幕对角线像素 / 屏幕对角线尺寸（英寸） 计算得到
例如：2880x1800 分辨率，14 英寸屏幕
DPI = √( 2880^2 + 1800^2 ) / 14 ≈ 242.58 DPI
因此，DPI 缩放的本质是：
Windows 通过调整逻辑像素（GDI 坐标系）到物理像素的映射关系
来让 UI 元素在高 DPI 显示器上看起来大小合适，而不是过小
"""


def get_screen_dpi_pywin32():
    """使用 Windows API 获取屏幕逻辑 DPI"""
    hdc = win32gui.GetDC(0)
    dpi_x = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSX)
    dpi_y = win32print.GetDeviceCaps(hdc, win32con.LOGPIXELSY)
    win32gui.ReleaseDC(0, hdc)
    return dpi_x, dpi_y


def get_screen_dpi_by_tkinter():
    """使用 Tkinter 获取屏幕逻辑 DPI"""
    root = Tk()
    root.withdraw()  # 隐藏窗口，避免闪烁
    try:
        # 1 inch 对应多少像素
        pixels = root.winfo_fpixels('1i')
        return round(pixels)
    finally:
        root.quit()
        root.destroy()


def get_physical_dpi(screen_width_px, screen_height_px, diagonal_inches):
    """
    计算物理 DPI
    :param screen_width_px: 水平像素
    :param screen_height_px: 垂直像素
    :param diagonal_inches: 屏幕对角线尺寸（英寸）
    """
    diagonal_pixels = math.sqrt(screen_width_px ** 2 + screen_height_px ** 2)
    return round(diagonal_pixels / diagonal_inches, 2)


def main():
    """测试各项功能"""
    scaling_width, scaling_height = get_logical_resolution()
    print(f"缩放后的分辨率: {scaling_width}x{scaling_height}")

    real_w, real_h = get_real_resolution()
    print(f"真实分辨率: {real_w}x{real_h}")

    scale_x, scale_y = get_screen_scaling()
    print(f"屏幕缩放比例: X={scale_x}, Y={scale_y}")

    print('pywin32 获取屏幕 DPI', get_screen_dpi_pywin32())

    print('Tkinter 获取屏幕 DPI =', get_screen_dpi_by_tkinter())

    # 14英寸屏幕
    physical_dpi = get_physical_dpi(real_w, real_h, 14)
    print(f"物理 DPI（14英寸屏幕）= {physical_dpi}")


if __name__ == '__main__':
    main()
