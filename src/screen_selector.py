# -*- coding: utf-8 -*-
"""
屏幕选区工具
使用 Tkinter 实现屏幕选区功能，允许用户通过鼠标拖动选择屏幕区域获取坐标
"""
import tkinter as tk
from dataclasses import dataclass


@dataclass
class BoxResult:
    """选区结果"""
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """计算右边界坐标"""
        return self.left + self.width

    @property
    def bottom(self) -> int:
        """计算下边界坐标"""
        return self.top + self.height


class BoxSelector:
    """使用 Tkinter 实现屏幕选区功能"""

    def __init__(self):
        self.root = tk.Tk()
        # 隐藏主窗口
        self.root.withdraw()

        # 创建全屏遮罩层
        self.top = tk.Toplevel(self.root)
        self.top.overrideredirect(True)  # 无边框
        self.top.attributes("-topmost", True)  # 置顶
        self.top.attributes("-alpha", 0.4)  # 半透明
        self.top.configure(bg="black")

        # 全屏尺寸
        self.screen_w = self.top.winfo_screenwidth()
        self.screen_h = self.top.winfo_screenheight()
        self.top.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        # 画布用来画框
        self.canvas = tk.Canvas(self.top,
                                bg="black",
                                highlightthickness=0,
                                cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Tkinter 事件绑定参数
        # https://docs.pysimplegui.com/en/latest/documentation/module/extending/event_bindings/
        # https://www.tcl-lang.org/man/tcl8.6/TkCmd/bind.htm
        self.canvas.bind("<ButtonPress-1>", self.on_press)  # 按下鼠标左键
        self.canvas.bind("<B1-Motion>", self.on_drag)  # 按住鼠标左键拖动
        self.canvas.bind("<ButtonRelease-1>", self.on_release)  # 释放鼠标左键

        # 存储矩形 ID 与坐标
        self.rect_id = None
        self.start_x = None
        self.start_y = None

        # 存储结果
        self.result: BoxResult | None = None

    def on_press(self, e):
        """
        鼠标按下时记录起始坐标并创建矩形
        这里直接用当前鼠标位置作为左上角坐标
        当然也可以根据需要调整为其他位置
        例如：self.start_x = e.x - 50
        这样矩形会以鼠标位置为中心向左偏移50像素
        """
        self.start_x, self.start_y = e.x, e.y
        # 画一个空心的矩形
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2, dash=(5, 5))

    def on_drag(self, e):
        """
        鼠标拖动时更新矩形
        这里直接用当前鼠标位置作为右下角坐标
        """
        self.canvas.coords(self.rect_id,
                           self.start_x, self.start_y, e.x, e.y)

    def on_release(self, e):
        """鼠标释放时计算选区坐标并关闭遮罩层"""
        end_x, end_y = e.x, e.y
        # 计算 left/top/width/height
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        # 创建 BoxResult 实例
        self.result = BoxResult(left=left, top=top, width=width, height=height)

        # 打印结果
        # print(f"left={left}, top={top}, width={width}, height={height}")

        # 关闭遮罩层并退出
        self.top.destroy()
        self.root.quit()

    def get_result(self):
        """获取选区结果"""
        return self.result

    def get_scaled_result(self, scale: float):
        """获取按比例缩放的选区结果"""
        if self.result is None:
            return None
        left = int(self.result.left * scale)
        top = int(self.result.top * scale)
        width = int(self.result.width * scale)
        height = int(self.result.height * scale)
        return BoxResult(left=left, top=top, width=width, height=height)
        # return left, top, width, height

    def run(self):
        """ 运行主循环  """
        try:
            self.root.mainloop()
        finally:
            # 销毁根窗口，释放 Tcl 解释器
            self.root.destroy()


if __name__ == "__main__":
    # 设置 DPI 感知，2 表示 Per-Monitor DPI Aware: 应用程序可以感知每个显示器的DPI设置。
    # 注：使用这个之后，就能正常获取坐标，也就不用再乘以缩放比例了。(仅限 Windows)
    # ctypes.windll.shcore.SetProcessDpiAwareness(2)

    selector = BoxSelector()
    selector.run()
    result = selector.get_result()
    print("选区结果：", result)

    from screen_utils import get_screen_scaling

    # 获取缩放
    scale_x, _ = get_screen_scaling()
    # 获取按比例缩放后的结果
    scaled_result = selector.get_scaled_result(scale_x)
    print(f"按比例 {scale_x} 缩放后的选区结果：", scaled_result)
