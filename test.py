import ctypes
from ctypes import wintypes

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

user32.GetWindowTextLengthW.restype = wintypes.INT
user32.GetWindowTextLengthW.argtypes = (
    wintypes.HWND,
)

user32.GetWindowTextW.restype = wintypes.INT
user32.GetWindowTextW.argtypes = (
    wintypes.HWND,
    wintypes.LPWSTR,
    wintypes.INT
)

user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (
    wintypes.HWND,
    wintypes.LPDWORD
)

def get_window_title(hwnd):
    """获取窗口标题"""
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buffer, length)
    return buffer.value

def get_process_name(hwnd):
    """获取窗口所属进程名"""
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    h_process = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
        False, pid
    )
    
    if h_process:
        try:
            buffer = ctypes.create_unicode_buffer(1024)
            ctypes.windll.psapi.GetModuleFileNameExW(
                h_process, None, buffer, ctypes.sizeof(buffer)
            )
            return buffer.value.split('\\')[-1]  # 只返回文件名
        finally:
            ctypes.windll.kernel32.CloseHandle(h_process)
    return ""

def enum_windows_callback(hwnd, lParam):
    """窗口枚举回调函数"""
    if user32.IsWindowVisible(hwnd):
        title = get_window_title(hwnd)
        if title:  # 只显示有标题的窗口
            process = get_process_name(hwnd)
            print(f"[{process}] {title}")
    return True

def list_windows():
    """列出所有可见窗口"""
    print("当前系统窗口列表:")
    print("=" * 50)
    enum_proc = WNDENUMPROC(enum_windows_callback)
    user32.EnumWindows(enum_proc, 0)

if __name__ == "__main__":
    list_windows()
