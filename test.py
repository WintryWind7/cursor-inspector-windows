import ctypes
import time
from ctypes import wintypes
from core.dist.window_func import get_window_info, get_window_title, get_process_name, enum_windows

# 启用 DPI 感知，确保在命令行环境下也能正确处理高分辨率显示器
# 暂时注释掉，先测试程序是否能正常运行
try:
    # 尝试使用 Windows 10+ 的 Per Monitor DPI Aware 模式
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except:
    try:
        # 回退到 Windows 8.1 的 System DPI Aware 模式
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass  # 如果都失败，保持默认行为

# Windows API定义
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 类型定义
WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,
    wintypes.LPARAM
)

# 函数定义
user32.EnumWindows.restype = wintypes.BOOL
user32.EnumWindows.argtypes = (
    WNDENUMPROC,
    wintypes.LPARAM
)

# 使用从 pyx 模块导入的函数，删除自定义实现

def enum_windows_callback(hwnd, lParam):
    """窗口枚举回调函数"""
    if user32.IsWindowVisible(hwnd):
        title = get_window_title(hwnd)
        process = get_process_name(hwnd)
        if title:  # 只显示有标题的窗口
            print(f"[{process}] {title}")
        else:
            print(f"[{process}] (无标题)")
    return True

def list_windows():
    """列出所有可见窗口"""
    print("当前系统窗口列表:")
    print("=" * 50)
    enum_proc = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(enum_proc, 0)

def find_deltaforce_window():
    """查找DeltaForceClient-Win64-Shipping.exe窗口并获取其信息"""
    target_process = "DeltaForceClient-Win64-Shipping.exe"
    found_windows = []
    
    # 使用 pyx 模块的 enum_windows 函数
    windows = enum_windows()
    
    for hwnd, title, process in windows:
        if process == target_process:
            print(f"DEBUG: 找到目标进程，窗口句柄: {hwnd}")
            print(f"DEBUG: 窗口标题: {title}")
            
            # 尝试多次获取，模拟 UI 运行时的状态
            for attempt in range(3):
                print(f"DEBUG: 第 {attempt + 1} 次尝试获取窗口信息...")
                window_info = get_window_info(hwnd)
                print(f"DEBUG: get_window_info 返回值: {window_info}")
                
                # 如果获取到正确的尺寸，就使用它
                if window_info and window_info['width'] > 1500 and window_info['height'] > 900:
                    print(f"DEBUG: 获取到正确的尺寸！")
                    break
                
                if attempt < 2:  # 不是最后一次尝试
                    time.sleep(0.1)  # 短暂延迟
            
            found_windows.append((hwnd, title, window_info))
    
    if found_windows:
        print(f"\n找到 {len(found_windows)} 个 {target_process} 窗口:")
        print("=" * 60)
        for i, (hwnd, title, window_info) in enumerate(found_windows, 1):
            print(f"窗口 {i}:")
            print(f"  句柄: {hwnd}")
            print(f"  标题: {title}")
            if window_info:
                print(f"  位置: 左={window_info['left']}, 上={window_info['top']}")
                print(f"  尺寸: 宽={window_info['width']}, 高={window_info['height']}")
                print(f"  右边界: {window_info['right']}, 下边界: {window_info['bottom']}")
            else:
                print("  无法获取窗口信息")
            print()
    else:
        print(f"\n未找到 {target_process} 窗口")
        print("请确保该程序正在运行")

if __name__ == "__main__":
    print("开始执行...")
    list_windows()
    print("开始查找 DeltaForce 窗口...")
    find_deltaforce_window()
    print("执行完成")
