# -*- coding: utf-8 -*-
"""
main.py - 屏幕OCR识别工具主界面

功能按钮：
- 开始：启动OCR识别循环
- 暂停：暂停OCR识别
- 日志开关：控制日志输出显示
- 设置框选：选择屏幕识别区域
"""
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from screen_ocr import grab_roi, roi2text
from screen_selector import BoxSelector, BoxResult
from screen_utils import get_screen_scaling


class MainApp:
    """主应用程序类"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("屏幕OCR识别工具")
        self.root.geometry("400x510")
        self.root.resizable(False, False)

        # 状态变量
        self.is_running = False  # 是否正在运行OCR
        self.log_enabled = True  # 是否显示日志
        self.roi_result: BoxResult | None = None  # 框选区域结果
        self.scale_x, self.scale_y = get_screen_scaling()  # 屏幕缩放比例
        self.area_visible = False  # 框选区域是否可见
        self.area_window: tk.Toplevel | None = None  # 显示框选区域的窗口

        # OCR配置变量
        self.char_whitelist = tk.StringVar()  # OCR字符白名单
        self.match_pattern = tk.StringVar()  # 正则匹配模式
        self.psm_var = tk.StringVar(value="单行文本")  # PSM模式
        # PSM选项映射：显示文本 -> PSM值
        self.psm_options = {
            "自动分割": 3,
            "文本块": 6,
            "单行文本": 7,
            "单个单词": 8,
            "单个字符": 10,
        }

        # OCR线程
        self.ocr_thread: threading.Thread | None = None
        self.stop_event = threading.Event()

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 按钮框架
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # 开始按钮
        self.start_btn = tk.Button(
            btn_frame, text="开始", width=10, height=2,
            command=self.on_start, bg="#4CAF50", fg="white"
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        # 暂停按钮
        self.pause_btn = tk.Button(
            btn_frame, text="暂停", width=10, height=2,
            command=self.on_pause, bg="#FF9800", fg="white",
            state=tk.DISABLED
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=5)

        # 日志开关按钮
        self.log_btn = tk.Button(
            btn_frame, text="日志开关: 开", width=10, height=2,
            command=self.on_toggle_log, bg="#2196F3", fg="white"
        )
        self.log_btn.grid(row=1, column=0, padx=5, pady=5)

        # 设置框选按钮
        self.select_btn = tk.Button(
            btn_frame, text="设置框选", width=10, height=2,
            command=self.on_select_area, bg="#9C27B0", fg="white"
        )
        self.select_btn.grid(row=1, column=1, padx=5, pady=5)

        # 显示区域按钮
        self.show_area_btn = tk.Button(
            btn_frame, text="显示区域: 关", width=10, height=2,
            command=self.on_toggle_area, bg="#607D8B", fg="white"
        )
        self.show_area_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # OCR配置框架
        config_frame = tk.LabelFrame(self.root, text="OCR配置", padx=10, pady=5)
        config_frame.pack(pady=5, padx=10, fill=tk.X)

        # 字符白名单输入框
        whitelist_label = tk.Label(config_frame, text="字符白名单:")
        whitelist_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        whitelist_entry = tk.Entry(
            config_frame, textvariable=self.char_whitelist, width=30
        )
        whitelist_entry.grid(row=0, column=1, pady=2, padx=5)

        # 匹配模式输入框
        pattern_label = tk.Label(config_frame, text="正则匹配模式:")
        pattern_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        pattern_entry = tk.Entry(
            config_frame, textvariable=self.match_pattern, width=30
        )
        pattern_entry.grid(row=1, column=1, pady=2, padx=5)

        # PSM模式下拉框
        psm_label = tk.Label(config_frame, text="识别模式:")
        psm_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        psm_combo = ttk.Combobox(
            config_frame, textvariable=self.psm_var,
            values=list(self.psm_options.keys()),
            state="readonly", width=27
        )
        psm_combo.grid(row=2, column=1, pady=2, padx=5)

        # 配置说明标签
        hint_label = tk.Label(
            config_frame,
            text="留空表示识别所有字符 / 返回完整结果",
            font=("Microsoft YaHei UI", 8), fg="#666666"
        )
        hint_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 2))

        # 状态标签
        self.status_label = tk.Label(
            self.root, text="状态: 未开始", font=("Arial", 10)
        )
        self.status_label.pack(pady=5)

        # 区域信息标签
        self.area_label = tk.Label(
            self.root, text="识别区域: 未设置", font=("Arial", 10)
        )
        self.area_label.pack(pady=5)

        # 日志文本框
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame, height=10, width=45,
            state=tk.DISABLED, font=("Consolas", 9)
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log(self, message):
        """输出日志到文本框"""
        if not self.log_enabled:
            return
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_start(self):
        """开始按钮点击事件"""
        if self.roi_result is None:
            messagebox.showwarning("提示", "请先设置识别区域！")
            return

        self.is_running = True
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 运行中...")
        self.log("OCR识别已启动")

        # 启动OCR线程
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.ocr_thread.start()

    def on_pause(self):
        """暂停按钮点击事件"""
        self.is_running = False
        self.stop_event.set()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.NORMAL)
        self.status_label.config(text="状态: 已暂停")
        self.log("OCR识别已暂停")

    def on_toggle_log(self):
        """日志开关按钮点击事件"""
        self.log_enabled = not self.log_enabled
        status = "开" if self.log_enabled else "关"
        self.log_btn.config(text=f"日志开关: {status}")

    def on_toggle_area(self):
        """显示/隐藏框选区域"""
        if self.roi_result is None:
            messagebox.showwarning("提示", "请先设置识别区域！")
            return

        self.area_visible = not self.area_visible
        status = "开" if self.area_visible else "关"
        self.show_area_btn.config(text=f"显示区域: {status}")

        if self.area_visible:
            self._show_area_window()
        else:
            self._hide_area_window()

    def _show_area_window(self):
        """显示框选区域边框窗口"""
        if self.area_window is not None:
            return

        # 需要用逻辑坐标（未缩放的）来定位窗口
        logical_left = int(self.roi_result.left / self.scale_x)
        logical_top = int(self.roi_result.top / self.scale_y)
        logical_width = int(self.roi_result.width / self.scale_x)
        logical_height = int(self.roi_result.height / self.scale_y)

        self.area_window = tk.Toplevel(self.root)
        self.area_window.overrideredirect(True)  # 无边框
        self.area_window.attributes("-topmost", True)  # 置顶
        self.area_window.attributes("-transparentcolor", "black")  # 黑色透明
        self.area_window.configure(bg="black")

        # 设置窗口位置和大小
        self.area_window.geometry(
            f"{logical_width}x{logical_height}+{logical_left}+{logical_top}"
        )

        # 创建画布画边框
        canvas = tk.Canvas(
            self.area_window, bg="black",
            highlightthickness=0, width=logical_width, height=logical_height
        )
        canvas.pack(fill=tk.BOTH, expand=True)

        # 画红色边框
        border_width = 3
        canvas.create_rectangle(
            border_width // 2, border_width // 2,
            logical_width - border_width // 2, logical_height - border_width // 2,
            outline="red", width=border_width
        )

    def _hide_area_window(self):
        """隐藏框选区域边框窗口"""
        if self.area_window is not None:
            self.area_window.destroy()
            self.area_window = None

    def on_select_area(self):
        """设置框选按钮点击事件"""
        # 先隐藏区域显示窗口
        self._hide_area_window()
        self.root.withdraw()  # 隐藏主窗口
        self.root.update()

        try:
            selector = BoxSelector()
            selector.run()
            result = selector.get_result()

            if result and result.width > 0 and result.height > 0:
                # 应用缩放比例
                self.roi_result = selector.get_scaled_result(self.scale_x)
                self.area_label.config(
                    text=f"识别区域: ({self.roi_result.left}, {self.roi_result.top}) "
                         f"{self.roi_result.width}x{self.roi_result.height}"
                )
                self.log(f"已设置识别区域: {self.roi_result}")
                # 如果区域显示是开启的，重新显示
                if self.area_visible:
                    self._show_area_window()
            else:
                self.log("框选取消或无效")
        except Exception as e:
            self.log(f"框选出错: {e}")
        finally:
            self.root.deiconify()  # 恢复显示主窗口

    def _ocr_loop(self):
        """OCR识别循环（在后台线程中运行）"""
        import time
        while not self.stop_event.is_set():
            try:
                # 截取ROI区域
                roi = grab_roi(
                    self.roi_result.left,
                    self.roi_result.top,
                    self.roi_result.width,
                    self.roi_result.height
                )

                # OCR识别（传入配置参数）
                whitelist = self.char_whitelist.get().strip() or None
                pattern = self.match_pattern.get().strip() or None
                psm = self.psm_options.get(self.psm_var.get(), 7)
                text = roi2text(roi, char_whitelist=whitelist, pattern=pattern, psm=psm)

                # 在主线程中更新UI
                self.root.after(0, self._update_ocr_result, text)

            except Exception as e:
                self.root.after(0, self.log, f"OCR出错: {e}")

            # 间隔1秒
            time.sleep(1)

    def _update_ocr_result(self, text):
        """更新OCR结果到UI"""
        if text:
            self.log(f"识别结果: {text}")
        else:
            self.log("未识别到有效内容")

    def run(self):
        """运行主循环"""
        self.root.mainloop()


def main():
    app = MainApp()
    app.run()


if __name__ == "__main__":
    main()
