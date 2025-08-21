from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QButtonGroup, QGroupBox,
                              QComboBox, QSizePolicy)
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtGui import QColor
import sys
import ctypes
from ctypes import wintypes
from core.dist.cursor_func import get_cursor_position, get_pixel_color, get_pixel_area
from core.dist.window_func import (get_foreground_window, get_window_info,
                                  find_window_by_name, get_screen_resolution,
                                  enum_windows)

# 手动定义缺失的 Windows 类型
wintypes.HWINEVENTHOOK = wintypes.HANDLE

class MouseInspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标检查器")
        self.setGeometry(100, 100, 600, 400)
        
        # 显示模式
        self.display_mode = "coord"  # coord/rgb/hsv
        self.selected_window = None  # 当前选中的窗口
        self.window_info = None      # 当前窗口信息
        self._win_event_hook = None  # WinEventHook 句柄
        self._win_event_proc = None  # 回调引用，防止被GC
        
        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # 左侧控制面板
        control_panel = QGroupBox("控制")
        control_panel.setMinimumWidth(180)
        control_panel.setMaximumWidth(240)
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(8, 8, 8, 8)
        control_layout.setSpacing(6)
        
        self.button_group = QButtonGroup()
        modes = [
            ("坐标模式", "coord"),
            ("RGB模式", "rgb"), 
            ("HSV模式", "hsv")
        ]
        
        # 窗口选择（仅保留下拉框）
        self.window_combo = QComboBox()
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        # 下拉框仅在展开时自适应显示全部，收起后尽量紧凑
        self.window_combo.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.window_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.window_combo.setMinimumWidth(140)
        self.window_combo.setMaximumWidth(220)
        control_layout.addWidget(self.window_combo)
        
        for text, mode in modes:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, m=mode: self.set_display_mode(m))
            control_layout.addWidget(btn)
            self.button_group.addButton(btn)
            if mode == "coord":
                btn.setChecked(True)
        
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # 右侧显示区域 - 直接分为上下两栏
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(8, 8, 8, 8)
        display_layout.setSpacing(8)
        
        # 上栏：系统信息
        upper_panel = QGroupBox("系统信息")
        upper_layout = QVBoxLayout()
        upper_layout.setContentsMargins(6, 6, 6, 6)
        upper_layout.setSpacing(0)  # 无间距，完全紧贴
        upper_layout.setSizeConstraint(QVBoxLayout.SetNoConstraint)  # 不强制约束大小
        
        self.screen_res_label = QLabel("")
        self.screen_res_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.screen_res_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.screen_res_label.setMaximumHeight(20)  # 限制高度
        
        # 分割线
        separator = QLabel("─" * 30)
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #888888; font-size: 9px; margin: 0px; padding: 0px;")
        separator.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        separator.setMaximumHeight(8)  # 限制分割线高度
        
        self.pos_label = QLabel("鼠标位置: ")
        self.pos_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.pos_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.pos_label.setMaximumHeight(20)  # 限制高度
        
        self.color_label = QLabel("颜色值: ")
        self.color_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.color_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.color_label.setMaximumHeight(20)  # 限制高度
        
        # 桌面分辨率在最上方，其他紧贴
        upper_layout.addWidget(self.screen_res_label)
        upper_layout.addWidget(separator)
        upper_layout.addWidget(self.pos_label)
        upper_layout.addWidget(self.color_label)
        upper_panel.setLayout(upper_layout)
        
        # 下栏：窗口信息
        lower_panel = QGroupBox("窗口信息")
        lower_layout = QVBoxLayout()
        lower_layout.setContentsMargins(6, 6, 6, 6)
        lower_layout.setSpacing(0)  # 无间距，完全紧贴
        
        self.window_pos_label = QLabel("")
        self.window_pos_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.window_pos_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.window_pos_label.setMaximumHeight(20)  # 限制高度
        
        # 重新创建相对位置和百分比标签
        self.rel_label = QLabel("")
        self.rel_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.rel_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.rel_label.setMaximumHeight(20)  # 限制高度
        
        self.percent_label = QLabel("")
        self.percent_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.percent_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 固定高度
        self.percent_label.setMaximumHeight(20)  # 限制高度
        
        lower_layout.addWidget(self.window_pos_label)
        lower_layout.addWidget(self.rel_label)
        lower_layout.addWidget(self.percent_label)
        lower_panel.setLayout(lower_layout)
        
        # 添加到主布局
        display_layout.addWidget(upper_panel, stretch=2)
        display_layout.addWidget(lower_panel, stretch=1)
        # 让右侧信息区紧凑且占剩余空间
        layout.addLayout(display_layout, stretch=1)
        
        # 初始化窗口列表
        self.refresh_window_list()
        
        # 初始化屏幕分辨率显示
        self.update_screen_resolution()
        
        # 初始化窗口位置显示
        self.update_window_position_display()
        
        # 定时器更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)  # 100ms更新一次

        # 监听屏幕分辨率/几何变化
        try:
            screen = self.screen()
            if screen is not None:
                screen.geometryChanged.connect(self._on_screen_geometry_changed)
        except Exception:
            pass

    def set_display_mode(self, mode):
        self.display_mode = mode
        self.update_display()

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        cmax = max(r, g, b)
        cmin = min(r, g, b)
        delta = cmax - cmin
        
        if delta == 0:
            h = 0
        elif cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * (((b - r) / delta) + 2)
        else:
            h = 60 * (((r - g) / delta) + 4)
            
        s = 0 if cmax == 0 else (delta / cmax)
        v = cmax
        return h, s*100, v*100

    def refresh_window_list(self):
        """刷新窗口列表"""
        self.window_combo.clear()
        self.window_combo.addItem("-- 请选择窗口 --", None)
        
        # 使用enum_windows获取所有可见窗口
        try:
            windows = enum_windows()
            for hwnd, title, process in windows:
                # 限制标题长度，避免下拉框过宽
                display_title = title[:50] + "..." if len(title) > 50 else title
                self.window_combo.addItem(f"[{process}] {display_title}", hwnd)
        except Exception as e:
            print(f"获取窗口列表失败: {e}")
            # 如果枚举失败，至少添加前台窗口
            hwnd = get_foreground_window()
            if hwnd:
                self.window_combo.addItem("前台窗口", hwnd)

    def on_window_selected(self, index):
        """窗口选择变化事件"""
        hwnd = self.window_combo.itemData(index)
        self.selected_window = hwnd
        if hwnd:
            try:
                self.window_info = get_window_info(hwnd)
                print(f"已选择窗口: {self.window_combo.currentText()}")
                print(f"窗口信息: {self.window_info}")
                # 启用 WinEventHook 监听窗口移动/大小变化
                self._install_win_event_hook()
                # 更新窗口位置显示
                self.update_window_position_display()
            except Exception as e:
                print(f"获取窗口信息失败: {e}")
                self.window_info = None
                self.window_pos_label.setText("")
        else:
            self.window_info = None
            self._uninstall_win_event_hook()
            self.window_pos_label.setText("")

    def update_display(self):
        pos = get_cursor_position()
        if pos:
            x, y = pos
            # 固定顶部位置显示鼠标坐标
            self.pos_label.setText(f"鼠标位置: X={x}, Y={y}")
            
            # 窗口内相对坐标与百分比常显
            rel_text = "窗口内位置: "
            percent_text = "百分比: "
            if not self.window_info:
                rel_text += "未选择窗口"
                percent_text += "未选择窗口"
            else:
                win_x, win_y = self.window_info['left'], self.window_info['top']
                win_w, win_h = self.window_info['width'], self.window_info['height']
                
                rel_x = x - win_x
                rel_y = y - win_y
                
                if 0 <= rel_x < win_w and 0 <= rel_y < win_h:
                    percent_x = round(rel_x / win_w, 4)
                    percent_y = round(rel_y / win_h, 4)
                    rel_text += f"X={rel_x}, Y={rel_y}"
                    percent_text += f"X={percent_x:.4f}, Y={percent_y:.4f}"
                else:
                    rel_text += "鼠标不在窗口范围内"
                    percent_text += "鼠标不在窗口范围内"
            self.rel_label.setText(rel_text)
            self.percent_label.setText(percent_text)
            
            color = get_pixel_color(x, y)
            if color:
                r, g, b = color
                if self.display_mode == "coord":
                    self.color_label.setText("")
                elif self.display_mode == "rgb":
                    self.color_label.setText(f"RGB: ({r}, {g}, {b})")
                else:  # hsv
                    h, s, v = self.rgb_to_hsv(r, g, b)
                    self.color_label.setText(f"HSV: ({h:.1f}°, {s:.1f}%, {v:.1f}%)")
            
            # 更新窗口位置显示（如果窗口信息发生变化）
            if self.window_info:
                self.update_window_position_display()

    # -------------------- WinEventHook 部分 --------------------
    def _on_screen_geometry_changed(self):
        """屏幕分辨率/几何变化，刷新已选窗口数据和分辨率显示"""
        # 更新屏幕分辨率显示
        self.update_screen_resolution()
        
        # 刷新已选窗口数据
        if self.selected_window:
            try:
                self.window_info = get_window_info(self.selected_window)
                self.update_window_position_display()
            except Exception:
                self.window_info = None

    def _install_win_event_hook(self):
        """安装 WinEventHook 监听窗口移动/大小改变，自动刷新记录的窗口信息"""
        if not self.selected_window:
            return
        if self._win_event_hook is not None:
            return

        user32 = ctypes.windll.user32

        EVENT_OBJECT_LOCATIONCHANGE = 0x800B
        WINEVENT_OUTOFCONTEXT = 0x0000
        WINEVENT_SKIPOWNPROCESS = 0x0002

        WinEventProcType = ctypes.WINFUNCTYPE(
            None, wintypes.HWINEVENTHOOK, wintypes.DWORD, wintypes.HWND,
            wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD
        )

        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            # 仅处理所选窗口的位置信息变化
            try:
                if hwnd and self.selected_window and int(hwnd) == int(self.selected_window):
                    self.window_info = get_window_info(self.selected_window)
                    # 更新窗口位置显示
                    self.update_window_position_display()
            except Exception:
                pass

        self._win_event_proc = WinEventProcType(callback)
        user32.SetWinEventHook.restype = wintypes.HWINEVENTHOOK
        user32.SetWinEventHook.argtypes = [
            wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE,
            WinEventProcType, wintypes.DWORD, wintypes.DWORD, wintypes.UINT
        ]

        self._win_event_hook = user32.SetWinEventHook(
            EVENT_OBJECT_LOCATIONCHANGE, EVENT_OBJECT_LOCATIONCHANGE,
            None, self._win_event_proc, 0, 0,
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        )

    def _uninstall_win_event_hook(self):
        """卸载 WinEventHook"""
        if self._win_event_hook:
            try:
                ctypes.windll.user32.UnhookWinEvent(self._win_event_hook)
            except Exception:
                pass
            self._win_event_hook = None

    def update_screen_resolution(self):
        """更新屏幕分辨率显示"""
        try:
            resolution = get_screen_resolution()
            if resolution:
                width, height = resolution
                self.screen_res_label.setText(f"桌面分辨率: {width} x {height}")
            else:
                self.screen_res_label.setText("桌面分辨率: 获取失败")
        except Exception:
            self.screen_res_label.setText("桌面分辨率: 获取失败")

    def update_window_position_display(self):
        """更新窗口位置显示"""
        # 窗口位置常显
        if not self.window_info:
            self.window_pos_label.setText("窗口位置: 未选择窗口")
            return
        
        try:
            win_x, win_y = self.window_info['left'], self.window_info['top']
            win_w, win_h = self.window_info['width'], self.window_info['height']
            
            # 通过窗口位置判断是否被最小化（最小化时坐标通常为负数）
            is_minimized = (win_x < 0 or win_y < 0)
            
            if is_minimized:
                self.window_pos_label.setText(f"窗口位置: ({win_x}, {win_y}) 尺寸: {win_w} x {win_h} [最小化]")
            else:
                self.window_pos_label.setText(f"窗口位置: ({win_x}, {win_y}) 尺寸: {win_w} x {win_h}")
        except Exception:
            self.window_pos_label.setText("窗口位置: 获取失败")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MouseInspectorWindow()
    window.show()
    sys.exit(app.exec())
