from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QButtonGroup, QGroupBox,
                              QComboBox, QSizePolicy)
from PySide6.QtCore import QTimer, Slot, Qt
from PySide6.QtGui import QColor
import sys
from core.dist.cursor_func import get_cursor_position, get_pixel_color, get_pixel_area
from core.dist.window_func import (get_foreground_window, get_window_info,
                                  find_window_by_name, get_screen_resolution,
                                  enum_windows)

class MouseInspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标检查器")
        self.setGeometry(100, 100, 600, 400)
        
        # 显示模式
        self.display_mode = "coord"  # coord/rgb/hsv
        self.selected_window = None  # 当前选中的窗口
        self.window_info = None      # 当前窗口信息
        
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
        
        # 右侧显示区域
        display_panel = QGroupBox("信息")
        display_layout = QVBoxLayout()
        display_layout.setContentsMargins(8, 8, 8, 8)
        display_layout.setSpacing(6)
        
        self.pos_label = QLabel("鼠标位置: ")
        self.pos_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.pos_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.rel_label = QLabel("")
        self.rel_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.percent_label = QLabel("")
        self.percent_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.color_label = QLabel("颜色值: ")
        self.color_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # 使用左对齐确保文本块不随布局扩展而漂移
        left_aligned = QVBoxLayout()
        left_aligned.setContentsMargins(0, 0, 0, 0)
        left_aligned.setSpacing(4)
        left_aligned.addWidget(self.pos_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        left_aligned.addWidget(self.rel_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        left_aligned.addWidget(self.percent_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        left_aligned.addWidget(self.color_label, alignment=Qt.AlignLeft | Qt.AlignTop)
        display_layout.addLayout(left_aligned)
        display_panel.setLayout(display_layout)
        # 让右侧信息区紧凑且占剩余空间
        layout.addWidget(display_panel, stretch=1)
        
        # 初始化窗口列表
        self.refresh_window_list()
        
        # 定时器更新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)  # 100ms更新一次

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
            except Exception as e:
                print(f"获取窗口信息失败: {e}")
                self.window_info = None
        else:
            self.window_info = None

    def update_display(self):
        pos = get_cursor_position()
        if pos:
            x, y = pos
            # 固定顶部位置显示鼠标坐标
            self.pos_label.setText(f"鼠标位置: X={x}, Y={y}")
            
            # 窗口内相对坐标与百分比独立行显示
            rel_text = ""
            percent_text = ""
            if self.window_info:
                win_x, win_y = self.window_info['left'], self.window_info['top']
                win_w, win_h = self.window_info['width'], self.window_info['height']
                
                rel_x = x - win_x
                rel_y = y - win_y
                
                if 0 <= rel_x < win_w and 0 <= rel_y < win_h:
                    percent_x = round(rel_x / win_w, 4)
                    percent_y = round(rel_y / win_h, 4)
                    rel_text = f"窗口内位置: X={rel_x}, Y={rel_y}"
                    percent_text = f"百分比: X={percent_x:.4f}, Y={percent_y:.4f}"
                else:
                    rel_text = "鼠标不在窗口范围内"
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

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MouseInspectorWindow()
    window.show()
    sys.exit(app.exec())
