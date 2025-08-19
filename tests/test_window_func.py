import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'dist')))

try:
    import window_func
    PYD_AVAILABLE = True
except ImportError:
    PYD_AVAILABLE = False

@unittest.skipUnless(PYD_AVAILABLE, "需要编译后的.pyd模块")
class TestWindowFunc(unittest.TestCase):
    def test_get_foreground_window(self):
        """测试获取前台窗口"""
        hwnd = window_func.get_foreground_window()
        self.assertIsNotNone(hwnd)
        self.assertGreater(hwnd, 0)

    def test_get_window_info(self):
        """测试获取窗口信息"""
        hwnd = window_func.get_foreground_window()
        info = window_func.get_window_info(hwnd)
        self.assertIsNotNone(info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertGreater(info['width'], 0)
        self.assertGreater(info['height'], 0)

    def test_get_window_title(self):
        """测试获取窗口标题"""
        hwnd = window_func.get_foreground_window()
        title = window_func.get_window_title(hwnd)
        print(f"\n窗口标题测试结果: {title}")
        self.assertIsInstance(title, str)

    def test_get_process_name(self):
        """测试获取进程名"""
        hwnd = window_func.get_foreground_window()
        process = window_func.get_process_name(hwnd)
        print(f"\n进程名测试结果: {process}")
        self.assertIsInstance(process, str)
        self.assertTrue(process.endswith('.exe'))

    def test_enum_windows(self):
        """测试枚举窗口"""
        windows = window_func.enum_windows()
        print(f"\n枚举窗口测试结果(共{len(windows)}个窗口):")
        for i, (hwnd, title, process) in enumerate(windows[:3]):  # 只打印前3个窗口
            print(f"窗口{i+1}: hwnd={hwnd}, title='{title}', process='{process}'")
        self.assertIsInstance(windows, list)
        if windows:  # 可能有前台窗口
            hwnd, title, process = windows[0]
            self.assertGreater(hwnd, 0)
            self.assertIsInstance(title, str)
            self.assertIsInstance(process, str)

    def test_enum_windows_compare_with_test_py(self):
        """测试枚举窗口结果与test.py的逻辑对比"""
        # 获取pyx模块的枚举结果
        pyx_windows = window_func.enum_windows()
        
        # 模拟test.py的逻辑获取结果
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
        
        test_py_windows = []
        
        def enum_windows_callback(hwnd, lParam):
            """窗口枚举回调函数"""
            if user32.IsWindowVisible(hwnd):
                title = get_window_title(hwnd)
                if title:  # 只显示有标题的窗口
                    process = get_process_name(hwnd)
                    test_py_windows.append((hwnd, title, process))
            return True
        
        # 执行test.py的枚举逻辑
        enum_proc = WNDENUMPROC(enum_windows_callback)
        user32.EnumWindows(enum_proc, 0)
        
        print(f"\n对比测试结果:")
        print(f"pyx模块枚举窗口数量: {len(pyx_windows)}")
        print(f"test.py逻辑枚举窗口数量: {len(test_py_windows)}")
        
        # 验证两个结果的基本一致性
        self.assertGreater(len(pyx_windows), 0, "pyx模块应该能枚举到窗口")
        self.assertGreater(len(test_py_windows), 0, "test.py逻辑应该能枚举到窗口")
        
        # 检查数量是否相近（允许有小的差异，因为枚举时机可能不同）
        self.assertAlmostEqual(len(pyx_windows), len(test_py_windows), delta=5, 
                              msg="两个方法枚举的窗口数量应该相近")
        
        # 检查前几个窗口的标题是否一致（如果存在的话）
        if pyx_windows and test_py_windows:
            pyx_titles = [title for _, title, _ in pyx_windows[:5]]
            test_titles = [title for _, title, _ in test_py_windows[:5]]
            
            print(f"pyx模块前5个窗口标题: {pyx_titles}")
            print(f"test.py逻辑前5个窗口标题: {test_titles}")
            
            # 检查是否有重叠的窗口标题
            common_titles = set(pyx_titles) & set(test_titles)
            self.assertGreater(len(common_titles), 0, 
                              "两个方法应该能找到一些相同的窗口")

if __name__ == "__main__":
    unittest.main()
