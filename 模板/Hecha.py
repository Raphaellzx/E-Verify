import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font, PanedWindow, colorchooser
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from urllib.parse import urlparse
import time
from datetime import datetime
import threading
import queue
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import re

class EnhancedWebpageScreenshotTool:
    def __init__(self):
        self.save_path = None
        self.driver = None
        self.processing = False
        self.task_queue = queue.Queue()
        self.completed_count = 0
        self.total_count = 0
        
        # 配置文件路径
        self.config_file = "screenshot_config.json"
        
        # 存储网址和自定义名称的映射
        self.url_name_mapping = {}
        
        # 字体相关
        self.default_font = None
        self.load_fonts()
        
        self.root = tk.Tk()
        self.root.title("批量网页截图工具（优化版）")
        self.root.geometry("1000x900")
        
        # 设置窗口图标
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 设置窗口最小尺寸
        self.root.minsize(900, 700)
        
        self.setup_ui()
        self.load_config()
        
    def load_fonts(self):
        """加载字体"""
        try:
            # 尝试加载系统字体
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows系统字体路径
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                    "C:/Windows/Fonts/simhei.ttf",  # 黑体
                    "C:/Windows/Fonts/arial.ttf",  # Arial
                ]
            elif system == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/PingFang.ttc",  # 苹方
                    "/System/Library/Fonts/Arial.ttf",
                    "/Library/Fonts/Arial.ttf",
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 测试字体是否可用
                        test_font = ImageFont.truetype(font_path, 12)
                        self.default_font = font_path
                        print(f"使用字体: {font_path}")
                        break
                    except:
                        continue
            
            # 如果没找到可用字体，使用PIL默认字体
            if not self.default_font:
                self.default_font = ImageFont.load_default()
                print("使用默认字体")
                
        except Exception as e:
            print(f"字体加载失败: {e}")
            self.default_font = ImageFont.load_default()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建可滚动的画布容器
        canvas_container = tk.Frame(main_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布和滚动条
        canvas = tk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 现在在scrollable_frame中添加所有控件
        self.create_widgets(scrollable_frame)
    
    def create_widgets(self, parent):
        """创建所有控件"""
        # 标题
        title_label = ttk.Label(
            parent, 
            text="批量网页截图工具（优化版）", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # 保存位置
        save_frame = ttk.Frame(parent)
        save_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(save_frame, text="保存位置:").pack(side=tk.LEFT)
        self.save_path_var = tk.StringVar()
        save_path_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, width=70)
        save_path_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(
            save_frame, 
            text="选择", 
            command=self.select_save_directory,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # 等待时间设置
        wait_frame = ttk.Frame(parent)
        wait_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=10)
        
        ttk.Label(wait_frame, text="等待时间(秒):").pack(side=tk.LEFT)
        
        self.wait_time_var = tk.DoubleVar(value=3.0)
        wait_time_spinbox = ttk.Spinbox(
            wait_frame,
            from_=1,
            to=60,
            increment=0.5,
            textvariable=self.wait_time_var,
            width=8
        )
        wait_time_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(wait_frame, text="秒").pack(side=tk.LEFT)
        
        # 命名选项
        naming_frame = ttk.LabelFrame(parent, text="文件命名选项", padding="10")
        naming_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=10)
        
        self.naming_mode_var = tk.StringVar(value="custom")
        naming_radio_frame = ttk.Frame(naming_frame)
        naming_radio_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            naming_radio_frame,
            text="使用自定义命名",
            variable=self.naming_mode_var,
            value="custom",
            command=self.on_naming_mode_changed
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            naming_radio_frame,
            text="自动命名（基于网址）",
            variable=self.naming_mode_var,
            value="auto",
            command=self.on_naming_mode_changed
        ).pack(side=tk.LEFT, padx=10)
        
        # 自动命名选项（默认隐藏）
        self.auto_naming_frame = ttk.Frame(naming_frame)
        self.auto_naming_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.auto_naming_frame, text="自动命名格式:").pack(side=tk.LEFT)
        self.auto_naming_format_var = tk.StringVar(value="domain_timestamp")
        auto_naming_combo = ttk.Combobox(
            self.auto_naming_frame,
            textvariable=self.auto_naming_format_var,
            values=[
                "域名_时间戳",
                "域名_序号_时间戳",
                "完整网址_时间戳",
                "仅域名",
                "序号_域名"
            ],
            width=20,
            state="readonly"
        )
        auto_naming_combo.pack(side=tk.LEFT, padx=5)
        
        # 默认隐藏自动命名选项
        self.auto_naming_frame.pack_forget()
        
        # 网址和命名表格 - 使用PanedWindow实现可调整的分割
        table_frame = ttk.LabelFrame(parent, text="网址与自定义命名", padding="5")
        table_frame.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=10)
        
        # 配置表格框架的权重
        parent.grid_rowconfigure(4, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 创建可调整的分割窗口
        paned = PanedWindow(table_frame, orient=tk.HORIZONTAL, sashwidth=10, sashrelief=tk.RAISED)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # 网址列
        url_container = ttk.Frame(paned)
        paned.add(url_container)
        
        ttk.Label(url_container, text="网址 (每行一个)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        # 网址文本框
        url_text_frame = ttk.Frame(url_container)
        url_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.url_text = scrolledtext.ScrolledText(
            url_text_frame, 
            width=45, 
            height=15,  # 增加高度
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.url_text.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件，当网址变化时自动生成建议名称
        self.url_text.bind("<KeyRelease>", self.on_url_text_changed)
        
        # 网址按钮
        url_buttons_frame = ttk.Frame(url_container)
        url_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            url_buttons_frame,
            text="导入网址",
            command=self.import_urls_from_file
        ).pack(side=tk.LEFT, padx=2)
        
        # 名称列
        name_container = ttk.Frame(paned)
        paned.add(name_container)
        
        ttk.Label(name_container, text="自定义名称 (每行一个)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 2))
        
        # 名称文本框
        name_text_frame = ttk.Frame(name_container)
        name_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.name_text = scrolledtext.ScrolledText(
            name_text_frame, 
            width=35, 
            height=15,  # 增加高度
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        self.name_text.pack(fill=tk.BOTH, expand=True)
        
        # 名称按钮
        name_buttons_frame = ttk.Frame(name_container)
        name_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            name_buttons_frame,
            text="自动生成",
            command=self.auto_generate_names
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            name_buttons_frame,
            text="清空",
            command=self.clear_names
        ).pack(side=tk.LEFT, padx=2)
        
        # 表格操作按钮
        table_buttons_frame = ttk.Frame(table_frame)
        table_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            table_buttons_frame,
            text="添加示例",
            command=self.add_example_urls
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            table_buttons_frame,
            text="预览命名",
            command=self.preview_filenames
        ).pack(side=tk.LEFT, padx=2)
        
        # 水印选项
        watermark_frame = ttk.LabelFrame(parent, text="水印设置", padding="10")
        watermark_frame.grid(row=5, column=0, columnspan=4, sticky="ew", pady=10)
        
        # 水印启用选项
        self.watermark_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            watermark_frame,
            text="启用水印",
            variable=self.watermark_enabled_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2, columnspan=2)
        
        # 水印内容
        ttk.Label(watermark_frame, text="水印格式:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.watermark_format_var = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
        watermark_format_combo = ttk.Combobox(
            watermark_frame,
            textvariable=self.watermark_format_var,
            values=[
                "%Y-%m-%d %H:%M:%S",
                "%Y年%m月%d日 %H:%M:%S",
                "%Y/%m/%d %H:%M",
                "%Y-%m-%d",
                "%H:%M:%S",
                "Screenshot: %Y-%m-%d %H:%M:%S",
                "无日期"
            ],
            width=25,
            state="readonly"
        )
        watermark_format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 水印颜色选择
        ttk.Label(watermark_frame, text="水印颜色:").grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # 创建颜色选择框架
        color_frame = ttk.Frame(watermark_frame)
        color_frame.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 预定义颜色选项
        self.watermark_color_var = tk.StringVar(value="白色")
        color_options = ["白色", "黑色", "红色", "蓝色", "绿色", "黄色", "紫色", "橙色", "灰色", "自定义..."]
        color_combo = ttk.Combobox(
            color_frame,
            textvariable=self.watermark_color_var,
            values=color_options,
            width=12,
            state="readonly"
        )
        color_combo.pack(side=tk.LEFT, padx=5)
        color_combo.bind("<<ComboboxSelected>>", self.on_color_selected)
        
        # 自定义颜色预览框
        self.color_preview = tk.Frame(color_frame, width=30, height=20, bg="white", relief=tk.RIDGE, bd=2)
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        # 自定义颜色按钮
        self.custom_color_button = ttk.Button(
            color_frame,
            text="选择颜色",
            command=self.choose_custom_color,
            width=10
        )
        self.custom_color_button.pack(side=tk.LEFT, padx=5)
        
        # 默认隐藏自定义颜色按钮
        self.custom_color_button.pack_forget()
        
        # 存储自定义颜色值
        self.custom_color = (255, 255, 255)  # 默认白色
        
        # 水印位置
        ttk.Label(watermark_frame, text="水印位置:").grid(row=3, column=0, sticky=tk.W, pady=2)
        
        self.watermark_position_var = tk.StringVar(value="top-right")
        position_frame = ttk.Frame(watermark_frame)
        position_frame.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        positions = [
            ("右上角", "top-right"),
            ("右下角", "bottom-right"),
            ("左上角", "top-left"),
            ("左下角", "bottom-left"),
            ("居中", "center")
        ]
        
        for i, (text, value) in enumerate(positions):
            ttk.Radiobutton(
                position_frame,
                text=text,
                variable=self.watermark_position_var,
                value=value
            ).grid(row=0, column=i, padx=5)
        
        # 水印透明度
        ttk.Label(watermark_frame, text="透明度:").grid(row=4, column=0, sticky=tk.W, pady=2)
        
        opacity_frame = ttk.Frame(watermark_frame)
        opacity_frame.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        self.watermark_opacity_var = tk.DoubleVar(value=0.7)
        opacity_scale = ttk.Scale(
            opacity_frame,
            from_=0.1,
            to=1.0,
            variable=self.watermark_opacity_var,
            orient=tk.HORIZONTAL,
            length=150
        )
        opacity_scale.pack(side=tk.LEFT, padx=5)
        
        self.opacity_label = ttk.Label(opacity_frame, text="70%")
        self.opacity_label.pack(side=tk.LEFT)
        
        opacity_scale.configure(command=self.update_opacity_label)
        
        # 浏览器选项
        browser_frame = ttk.LabelFrame(parent, text="浏览器选项", padding="10")
        browser_frame.grid(row=6, column=0, columnspan=4, sticky="ew", pady=10)
        
        option_buttons_frame = ttk.Frame(browser_frame)
        option_buttons_frame.pack(fill=tk.X)
        
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            option_buttons_frame,
            text="后台运行（不显示浏览器窗口）",
            variable=self.headless_var
        ).pack(side=tk.LEFT, padx=10)
        
        self.full_page_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            option_buttons_frame,
            text="截取完整页面",
            variable=self.full_page_var
        ).pack(side=tk.LEFT, padx=10)
        
        self.keep_browser_open_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            option_buttons_frame,
            text="完成后保持浏览器打开",
            variable=self.keep_browser_open_var
        ).pack(side=tk.LEFT, padx=10)
        
        # 进度条和状态
        self.progress = ttk.Progressbar(
            parent, 
            mode='determinate',
            length=950
        )
        self.progress.grid(row=7, column=0, columnspan=4, pady=(15, 5), sticky="ew")
        
        # 状态显示
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(
            parent, 
            textvariable=self.status_var,
            font=("Arial", 10)
        )
        status_label.grid(row=8, column=0, columnspan=4, pady=(0, 5))
        
        # 统计信息
        self.stats_var = tk.StringVar(value="等待任务...")
        stats_label = ttk.Label(
            parent, 
            textvariable=self.stats_var,
            font=("Arial", 9)
        )
        stats_label.grid(row=9, column=0, columnspan=4, pady=(0, 10))
        
        # 日志输出
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        log_frame.grid(row=10, column=0, columnspan=4, sticky="nsew", pady=10)
        
        parent.grid_rowconfigure(10, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=8,  # 增加高度
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 日志操作按钮
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            log_buttons_frame,
            text="清空日志",
            command=self.clear_log
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            log_buttons_frame,
            text="复制日志",
            command=self.copy_log
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            log_buttons_frame,
            text="保存日志",
            command=self.save_log
        ).pack(side=tk.LEFT, padx=2)
        
        # 底部按钮
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=11, column=0, columnspan=4, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="开始截图",
            command=self.start_batch_capture,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_capture
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="打开保存目录",
            command=self.open_save_directory
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="同步滚动",
            command=self.toggle_sync_scroll,
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="退出",
            command=self.exit_application
        ).pack(side=tk.LEFT, padx=10)
        
        # 同步滚动状态
        self.sync_scroll_enabled = False
        
        # 创建样式
        self.create_styles()
    
    def create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        style.configure("Accent.TButton", background="#4CAF50", foreground="white")
        
        # 配置滚动条样式
        style.configure("Vertical.TScrollbar", arrowsize=16, width=16)
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        opacity_percent = int(float(value) * 100)
        self.opacity_label.config(text=f"{opacity_percent}%")
    
    def on_color_selected(self, event=None):
        """颜色选择改变时触发"""
        selected_color = self.watermark_color_var.get()
        
        # 颜色映射表
        color_map = {
            "白色": (255, 255, 255),
            "黑色": (0, 0, 0),
            "红色": (255, 0, 0),
            "蓝色": (0, 0, 255),
            "绿色": (0, 255, 0),
            "黄色": (255, 255, 0),
            "紫色": (128, 0, 128),
            "橙色": (255, 165, 0),
            "灰色": (128, 128, 128)
        }
        
        if selected_color == "自定义...":
            # 显示自定义颜色按钮
            self.custom_color_button.pack(side=tk.LEFT, padx=5)
            # 使用当前自定义颜色
            r, g, b = self.custom_color
            self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
        else:
            # 隐藏自定义颜色按钮
            self.custom_color_button.pack_forget()
            # 更新颜色预览
            if selected_color in color_map:
                r, g, b = color_map[selected_color]
                self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
    
    def choose_custom_color(self):
        """选择自定义颜色"""
        # 打开颜色选择器
        color_code = colorchooser.askcolor(title="选择水印颜色", initialcolor=f'#{self.custom_color[0]:02x}{self.custom_color[1]:02x}{self.custom_color[2]:02x}')
        
        if color_code[0]:  # 用户选择了颜色
            r, g, b = [int(c) for c in color_code[0]]
            self.custom_color = (r, g, b)
            self.color_preview.config(bg=color_code[1])
            
            # 更新颜色选择器显示
            self.watermark_color_var.set("自定义...")
            self.log_message(f"已选择自定义颜色: RGB({r}, {g}, {b})")
    
    def clear_names(self):
        """清空名称文本框"""
        if messagebox.askyesno("确认", "确定要清空所有名称吗？"):
            self.name_text.delete("1.0", tk.END)
            self.log_message("名称已清空")
    
    def clear_log(self):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空日志吗？"):
            self.log_text.delete("1.0", tk.END)
            self.log_message("日志已清空")
    
    def copy_log(self):
        """复制日志内容"""
        log_content = self.log_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self.log_message("日志已复制到剪贴板")
    
    def save_log(self):
        """保存日志到文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                log_content = self.log_text.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.log_message(f"日志已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败:\n{str(e)}")
    
    def toggle_sync_scroll(self):
        """切换同步滚动状态"""
        self.sync_scroll_enabled = not self.sync_scroll_enabled
        
        if self.sync_scroll_enabled:
            self.log_message("已启用同步滚动")
            # 这里可以添加同步滚动的实现
            # 但由于两个ScrolledText控件内部有滚动条，实现较复杂
            # 这里只提供状态切换，实际同步需要更复杂的实现
        else:
            self.log_message("已禁用同步滚动")
    
    def on_naming_mode_changed(self):
        """命名模式改变"""
        if self.naming_mode_var.get() == "auto":
            self.auto_naming_frame.pack(fill=tk.X, pady=5)
            self.name_text.config(state="disabled")
            self.log_message("已切换到自动命名模式")
        else:
            self.auto_naming_frame.pack_forget()
            self.name_text.config(state="normal")
            self.log_message("已切换到自定义命名模式")
    
    def on_url_text_changed(self, event=None):
        """网址文本框内容改变时触发"""
        # 如果启用了自动命名，则自动生成名称
        if self.naming_mode_var.get() == "auto":
            self.auto_generate_names()
    
    def select_save_directory(self):
        """选择保存目录"""
        path = filedialog.askdirectory(
            title="选择截图保存位置",
            initialdir=self.save_path_var.get() or os.path.expanduser("~")
        )
        if path:
            self.save_path_var.set(path)
            self.save_path = path
            self.save_config()
    
    def import_urls_from_file(self):
        """从文件导入网址"""
        file_path = filedialog.askopenfilename(
            title="选择网址文件",
            filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 清空现有内容
                self.url_text.delete("1.0", tk.END)
                self.name_text.delete("1.0", tk.END)
                
                urls = []
                names = []
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):  # 忽略注释和空行
                        # 尝试解析不同格式
                        if ',' in line:
                            # CSV格式：网址,名称
                            parts = line.split(',', 1)
                            url = parts[0].strip()
                            name = parts[1].strip() if len(parts) > 1 else ""
                        elif '\t' in line:
                            # Tab分隔格式
                            parts = line.split('\t', 1)
                            url = parts[0].strip()
                            name = parts[1].strip() if len(parts) > 1 else ""
                        else:
                            # 只有网址
                            url = line
                            name = ""
                        
                        if url:
                            urls.append(url)
                            names.append(name)
                
                # 更新文本框
                for url in urls:
                    self.url_text.insert(tk.END, url + "\n")
                
                for name in names:
                    self.name_text.insert(tk.END, name + "\n")
                
                self.log_message(f"已从 {os.path.basename(file_path)} 导入 {len(urls)} 个网址")
                
                # 如果是自动命名模式，自动生成名称
                if self.naming_mode_var.get() == "auto" and urls:
                    self.auto_generate_names()
                
            except Exception as e:
                messagebox.showerror("错误", f"导入文件失败:\n{str(e)}")
    
    def auto_generate_names(self):
        """自动生成名称"""
        urls = self.get_urls_from_text()
        
        if not urls:
            messagebox.showwarning("警告", "请先输入网址")
            return
        
        # 清空名称文本框
        self.name_text.config(state="normal")
        self.name_text.delete("1.0", tk.END)
        
        for i, url in enumerate(urls):
            # 生成建议名称
            suggested_name = self.suggest_filename_from_url(url, i)
            self.name_text.insert(tk.END, suggested_name + "\n")
        
        if self.naming_mode_var.get() == "auto":
            self.name_text.config(state="disabled")
        
        self.log_message(f"已为 {len(urls)} 个网址生成建议名称")
    
    def suggest_filename_from_url(self, url, index):
        """根据网址生成建议文件名"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            
            # 提取路径部分作为名称
            path = parsed_url.path.strip('/')
            if path:
                # 只取最后一部分作为名称
                name_parts = path.split('/')
                last_part = name_parts[-1]
                
                # 移除扩展名和特殊字符
                last_part = re.sub(r'\.[a-zA-Z0-9]+$', '', last_part)  # 移除扩展名
                last_part = re.sub(r'[^\w\s-]', '', last_part)  # 移除特殊字符
                last_part = re.sub(r'[-_]+', '_', last_part)  # 标准化分隔符
                
                if last_part:
                    suggested = f"{domain}_{last_part}"
                else:
                    suggested = domain
            else:
                suggested = domain
            
            # 限制长度
            if len(suggested) > 40:
                suggested = suggested[:40]
            
            return suggested
            
        except:
            return f"website_{index+1}"
    
    def add_example_urls(self):
        """添加示例网址"""
        examples = [
            ("https://www.baidu.com", "百度首页"),
            ("https://www.google.com", "谷歌搜索"),
            ("https://github.com", "GitHub"),
            ("https://www.python.org", "Python官网"),
            ("https://news.sina.com.cn", "新浪新闻"),
            ("https://www.zhihu.com", "知乎首页"),
            ("https://www.bilibili.com", "哔哩哔哩"),
            ("https://www.jd.com", "京东商城")
        ]
        
        # 清空现有内容
        self.url_text.delete("1.0", tk.END)
        self.name_text.delete("1.0", tk.END)
        
        for url, name in examples:
            self.url_text.insert(tk.END, url + "\n")
            self.name_text.insert(tk.END, name + "\n")
        
        self.log_message(f"已添加 {len(examples)} 个示例网址")
    
    def get_url_name_pairs(self):
        """获取网址和名称对"""
        urls = self.get_urls_from_text()
        
        if self.naming_mode_var.get() == "custom":
            names = self.get_names_from_text()
        else:
            # 自动命名模式
            names = []
            for i, url in enumerate(urls):
                if self.auto_naming_format_var.get() == "域名_时间戳":
                    names.append(self.suggest_filename_from_url(url, i))
                elif self.auto_naming_format_var.get() == "域名_序号_时间戳":
                    names.append(f"{self.suggest_filename_from_url(url, i)}_{i+1}")
                elif self.auto_naming_format_var.get() == "完整网址_时间戳":
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.replace('www.', '')
                    path = parsed_url.path.replace('/', '_').strip('_')
                    names.append(f"{domain}_{path}" if path else domain)
                elif self.auto_naming_format_var.get() == "仅域名":
                    parsed_url = urlparse(url)
                    names.append(parsed_url.netloc.replace('www.', ''))
                else:  # 序号_域名
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.replace('www.', '')
                    names.append(f"{i+1:03d}_{domain}")
        
        # 确保长度一致
        if len(names) < len(urls):
            for i in range(len(urls) - len(names)):
                names.append("")
        elif len(names) > len(urls):
            names = names[:len(urls)]
        
        return list(zip(urls, names))
    
    def get_urls_from_text(self):
        """从文本框获取网址列表"""
        text = self.url_text.get("1.0", tk.END).strip()
        if not text:
            return []
        
        urls = []
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if not line.startswith(('http://', 'https://')):
                    line = 'https://' + line
                urls.append(line)
        
        return urls
    
    def get_names_from_text(self):
        """从文本框获取名称列表"""
        text = self.name_text.get("1.0", tk.END).strip()
        if not text:
            return []
        
        names = []
        for line in text.split('\n'):
            line = line.strip()
            names.append(line)
        
        return names
    
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            if self.driver:
                return True
            
            edge_options = Options()
            
            if self.headless_var.get():
                edge_options.add_argument('--headless')
            
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--window-size=1920,1080')
            
            # 添加其他优化选项
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service()
            self.driver = webdriver.Edge(service=service, options=edge_options)
            
            # 设置页面加载策略
            self.driver.set_page_load_timeout(30)
            
            return True
            
        except Exception as e:
            self.log_message(f"浏览器启动失败: {str(e)}")
            messagebox.showerror("错误", f"无法启动Edge浏览器:\n{str(e)}")
            return False
    
    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符"""
        if not filename:
            return ""
        
        # 移除非法字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 移除多余的空格和下划线
        filename = re.sub(r'_{2,}', '_', filename)
        filename = re.sub(r'\s{2,}', ' ', filename)
        filename = filename.strip(' ._')
        
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename
    
    def generate_filename(self, url, custom_name, index):
        """生成文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 清理自定义名称
        if custom_name:
            custom_name = self.sanitize_filename(custom_name)
        
        if self.naming_mode_var.get() == "custom" and custom_name:
            # 自定义命名模式，使用用户指定的名称
            # 添加时间戳避免重复
            filename = f"{custom_name}_{timestamp}.png"
        else:
            # 自动命名模式或自定义名称为空
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace('www.', '')
                
                # 提取路径部分
                path = parsed_url.path.strip('/').replace('/', '_')
                
                # 组合文件名
                if path:
                    base_name = f"{domain}_{path}"
                else:
                    base_name = domain
                
                # 限制长度
                if len(base_name) > 50:
                    base_name = base_name[:50]
                
                # 添加序号和时间戳
                filename = f"{index+1:03d}_{base_name}_{timestamp}.png"
                
            except:
                # 如果URL解析失败，使用简单方式生成文件名
                filename = f"{index+1:03d}_screenshot_{timestamp}.png"
        
        # 再次清理确保没有非法字符
        return self.sanitize_filename(filename)
    
    def add_watermark_to_image(self, image_path):
        """为图片添加水印"""
        try:
            if not self.watermark_enabled_var.get():
                return True
            
            # 打开图片
            image = Image.open(image_path)
            
            # 获取图片尺寸
            width, height = image.size
            
            # 确定水印文本
            watermark_format = self.watermark_format_var.get()
            if watermark_format == "无日期":
                return True  # 不添加水印
            
            watermark_text = datetime.now().strftime(watermark_format)
            
            # 创建绘图对象
            draw = ImageDraw.Draw(image)
            
            # 确定字体大小（基于图片尺寸）
            font_size = max(int(min(width, height) * 0.02), 12)
            
            try:
                if isinstance(self.default_font, str):
                    font = ImageFont.truetype(self.default_font, font_size)
                else:
                    font = self.default_font
            except:
                font = ImageFont.load_default()
            
            # 计算文本尺寸
            try:
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                # 旧版PIL的兼容性处理
                try:
                    text_width, text_height = draw.textsize(watermark_text, font=font)
                except:
                    text_width = len(watermark_text) * font_size * 0.6
                    text_height = font_size
            
            # 确定水印位置
            position = self.watermark_position_var.get()
            padding = int(min(width, height) * 0.02)  # 边距
            
            if position == "top-right":
                x = width - text_width - padding
                y = padding
            elif position == "bottom-right":
                x = width - text_width - padding
                y = height - text_height - padding
            elif position == "top-left":
                x = padding
                y = padding
            elif position == "bottom-left":
                x = padding
                y = height - text_height - padding
            elif position == "center":
                x = (width - text_width) // 2
                y = (height - text_height) // 2
            else:
                x = width - text_width - padding
                y = padding
            
            # 根据选择的颜色设置水印颜色
            selected_color = self.watermark_color_var.get()
            
            # 颜色映射表
            color_map = {
                "白色": (255, 255, 255),
                "黑色": (0, 0, 0),
                "红色": (255, 0, 0),
                "蓝色": (0, 0, 255),
                "绿色": (0, 255, 0),
                "黄色": (255, 255, 0),
                "紫色": (128, 0, 128),
                "橙色": (255, 165, 0),
                "灰色": (128, 128, 128)
            }
            
            if selected_color == "自定义...":
                # 使用自定义颜色
                color = self.custom_color
            elif selected_color in color_map:
                # 使用预定义颜色
                color = color_map[selected_color]
            else:
                # 默认白色
                color = (255, 255, 255)
            
            # 计算透明度
            opacity = int(self.watermark_opacity_var.get() * 255)
            
            # 绘制水印文本
            draw.text((x, y), watermark_text, font=font, fill=color + (opacity,))
            
            # 保存图片
            image.save(image_path)
            
            return True
            
        except Exception as e:
            self.log_message(f"添加水印失败: {str(e)}")
            return False
    
    def preview_filenames(self):
        """预览文件名"""
        url_name_pairs = self.get_url_name_pairs()
        
        if not url_name_pairs:
            messagebox.showinfo("提示", "请先输入网址")
            return
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("文件名预览")
        preview_window.geometry("800x600")
        
        # 创建文本框架
        preview_frame = ttk.Frame(preview_window, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(preview_frame, text="文件名预览", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 创建带滚动条的文本区域
        preview_text = scrolledtext.ScrolledText(
            preview_frame,
            width=80,
            height=25,
            wrap=tk.WORD,
            font=("Courier", 10)
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加预览内容
        preview_text.insert(tk.END, "文件名预览:\n" + "="*60 + "\n\n")
        
        for i, (url, custom_name) in enumerate(url_name_pairs):
            filename = self.generate_filename(url, custom_name, i)
            preview_text.insert(tk.END, f"{i+1:3d}. {filename}\n")
            
            # 显示网址（截断过长的网址）
            url_display = url[:60] + "..." if len(url) > 60 else url
            preview_text.insert(tk.END, f"    网址: {url_display}\n")
            
            # 显示自定义名称（如果存在）
            if custom_name and self.naming_mode_var.get() == "custom":
                preview_text.insert(tk.END, f"    自定义名称: {custom_name}\n")
            
            preview_text.insert(tk.END, "\n")
        
        preview_text.config(state="disabled")
        
        # 关闭按钮
        ttk.Button(
            preview_frame,
            text="关闭",
            command=preview_window.destroy
        ).pack(pady=10)
    
    def capture_single_page(self, url, custom_name, index):
        """捕获单个页面截图"""
        try:
            self.log_message(f"[{index+1}/{self.total_count}] 正在访问: {url}")
            
            self.driver.get(url)
            
            # 等待指定时间
            wait_time = self.wait_time_var.get()
            self.log_message(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
            
            # 设置窗口大小
            if self.full_page_var.get():
                try:
                    total_height = self.driver.execute_script(
                        "return Math.max(document.body.scrollHeight, "
                        "document.body.offsetHeight, document.documentElement.clientHeight, "
                        "document.documentElement.scrollHeight, document.documentElement.offsetHeight)"
                    )
                    self.driver.set_window_size(1920, total_height)
                except:
                    self.driver.set_window_size(1920, 1080)
            
            # 生成文件名并保存
            filename = self.generate_filename(url, custom_name, index)
            save_file = os.path.join(self.save_path, filename)
            
            self.driver.save_screenshot(save_file)
            
            # 添加水印
            if self.watermark_enabled_var.get():
                self.log_message("正在添加水印...")
                self.add_watermark_to_image(save_file)
            
            self.completed_count += 1
            self.update_progress()
            
            self.log_message(f"✓ 截图已保存: {filename}")
            
            return True, filename
            
        except Exception as e:
            self.log_message(f"✗ 截图失败: {str(e)}")
            return False, str(e)
    
    def update_progress(self):
        """更新进度条和状态"""
        if self.total_count > 0:
            progress_value = (self.completed_count / self.total_count) * 100
            self.progress['value'] = progress_value
            
            self.stats_var.set(
                f"已完成: {self.completed_count}/{self.total_count} "
                f"({progress_value:.1f}%)"
            )
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # 自动滚动到底部
        
        # 同时更新状态栏
        self.status_var.set(message[:50] + "..." if len(message) > 50 else message)
        
        # 刷新界面
        self.root.update_idletasks()
    
    def start_batch_capture(self):
        """开始批量截图"""
        if self.processing:
            messagebox.showinfo("提示", "任务正在进行中...")
            return
        
        # 检查保存位置
        if not self.save_path_var.get():
            messagebox.showwarning("警告", "请先选择保存位置")
            return
        
        # 获取网址和名称对
        url_name_pairs = self.get_url_name_pairs()
        if not url_name_pairs:
            messagebox.showwarning("警告", "请输入至少一个网址")
            return
        
        # 检查保存目录是否存在
        self.save_path = self.save_path_var.get()
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        # 保存配置
        self.save_config()
        
        # 设置任务参数
        self.task_queue = queue.Queue()
        for url, name in url_name_pairs:
            self.task_queue.put((url, name))
        
        self.total_count = len(url_name_pairs)
        self.completed_count = 0
        self.processing = True
        
        # 重置进度条
        self.progress['value'] = 0
        self.progress['maximum'] = 100
        
        # 禁用开始按钮
        self.start_button['state'] = 'disabled'
        
        # 在新线程中执行任务
        thread = threading.Thread(target=self.process_batch)
        thread.daemon = True
        thread.start()
    
    def process_batch(self):
        """处理批量任务"""
        try:
            self.log_message(f"开始批量截图，共 {self.total_count} 个网址")
            
            # 设置浏览器
            if not self.setup_driver():
                self.processing = False
                self.start_button['state'] = 'normal'
                return
            
            index = 0
            while not self.task_queue.empty() and self.processing:
                url, custom_name = self.task_queue.get()
                success, result = self.capture_single_page(url, custom_name, index)
                index += 1
            
            # 任务完成
            if self.processing:
                self.log_message(f"批量截图完成！共处理 {self.completed_count} 个网址")
                
                # 检查是否需要关闭浏览器
                if not self.keep_browser_open_var.get():
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                        self.log_message("浏览器已关闭")
                else:
                    self.log_message("浏览器保持打开状态")
                
                # 播放完成提示音（可选）
                try:
                    import winsound
                    winsound.MessageBeep()
                except:
                    pass
                
                messagebox.showinfo("完成", f"批量截图完成！\n共处理 {self.completed_count} 个网址")
            
        except Exception as e:
            self.log_message(f"处理过程中发生错误: {str(e)}")
        
        finally:
            self.processing = False
            self.start_button['state'] = 'normal'
    
    def stop_capture(self):
        """停止截图任务"""
        if self.processing:
            if messagebox.askyesno("确认", "确定要停止当前任务吗？"):
                self.processing = False
                self.log_message("任务已停止")
                
                # 清空任务队列
                while not self.task_queue.empty():
                    self.task_queue.get()
    
    def open_save_directory(self):
        """打开保存目录"""
        if self.save_path and os.path.exists(self.save_path):
            try:
                os.startfile(self.save_path)  # Windows
            except:
                try:
                    import subprocess
                    subprocess.run(['open', self.save_path])  # macOS
                except:
                    try:
                        import subprocess
                        subprocess.run(['xdg-open', self.save_path])  # Linux
                    except:
                        self.log_message("无法打开保存目录")
        else:
            messagebox.showinfo("提示", "请先选择保存位置")
    
    def save_config(self):
        """保存配置到文件"""
        # 保存自定义颜色
        if self.watermark_color_var.get() == "自定义...":
            custom_color_str = f"{self.custom_color[0]},{self.custom_color[1]},{self.custom_color[2]}"
        else:
            custom_color_str = ""
        
        config = {
            'save_path': self.save_path_var.get(),
            'wait_time': self.wait_time_var.get(),
            'headless': self.headless_var.get(),
            'full_page': self.full_page_var.get(),
            'keep_browser_open': self.keep_browser_open_var.get(),
            'watermark_enabled': self.watermark_enabled_var.get(),
            'watermark_format': self.watermark_format_var.get(),
            'watermark_color': self.watermark_color_var.get(),
            'custom_color': custom_color_str,
            'watermark_position': self.watermark_position_var.get(),
            'watermark_opacity': self.watermark_opacity_var.get(),
            'naming_mode': self.naming_mode_var.get(),
            'auto_naming_format': self.auto_naming_format_var.get(),
            'urls': self.url_text.get("1.0", tk.END).strip(),
            'names': self.name_text.get("1.0", tk.END).strip()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.save_path_var.set(config.get('save_path', ''))
                self.wait_time_var.set(config.get('wait_time', 3.0))
                self.headless_var.set(config.get('headless', True))
                self.full_page_var.set(config.get('full_page', True))
                self.keep_browser_open_var.set(config.get('keep_browser_open', True))
                self.watermark_enabled_var.set(config.get('watermark_enabled', True))
                self.watermark_format_var.set(config.get('watermark_format', "%Y-%m-%d %H:%M:%S"))
                self.watermark_color_var.set(config.get('watermark_color', "白色"))
                self.watermark_position_var.set(config.get('watermark_position', "top-right"))
                self.watermark_opacity_var.set(config.get('watermark_opacity', 0.7))
                self.naming_mode_var.set(config.get('naming_mode', "custom"))
                self.auto_naming_format_var.set(config.get('auto_naming_format', "domain_timestamp"))
                
                # 加载自定义颜色
                custom_color_str = config.get('custom_color', '')
                if custom_color_str:
                    r, g, b = map(int, custom_color_str.split(','))
                    self.custom_color = (r, g, b)
                    if self.watermark_color_var.get() == "自定义...":
                        self.color_preview.config(bg=f'#{r:02x}{g:02x}{b:02x}')
                
                urls = config.get('urls', '')
                if urls:
                    self.url_text.delete("1.0", tk.END)
                    self.url_text.insert(tk.END, urls)
                
                names = config.get('names', '')
                if names:
                    self.name_text.delete("1.0", tk.END)
                    self.name_text.insert(tk.END, names)
                
                # 更新透明度标签
                self.update_opacity_label(self.watermark_opacity_var.get())
                
                # 更新颜色预览
                self.on_color_selected()
                
                # 更新界面状态
                self.on_naming_mode_changed()
                
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def exit_application(self):
        """退出应用程序"""
        if self.processing:
            if not messagebox.askyesno("确认", "任务正在进行中，确定要退出吗？"):
                return
        
        # 保存配置
        self.save_config()
        
        # 关闭浏览器
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.root.quit()
    
    def run(self):
        """运行主程序"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        self.root.mainloop()

def main():
    app = EnhancedWebpageScreenshotTool()
    app.run()

if __name__ == "__main__":
    main()