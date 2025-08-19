import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'dist')))

try:
    import cursor_func
    import window_func
    PYD_AVAILABLE = True
except ImportError:
    PYD_AVAILABLE = False

@unittest.skipUnless(PYD_AVAILABLE, "需要编译后的.pyd模块")
class TestCursorFunc(unittest.TestCase):
    def test_get_cursor_position(self):
        pos = cursor_func.get_cursor_position()
        self.assertIsNotNone(pos)
        self.assertEqual(len(pos), 2)
        self.assertIsInstance(pos[0], int)
        self.assertIsInstance(pos[1], int)

    def test_get_pixel_color(self):
        # 测试屏幕左上角像素
        color = cursor_func.get_pixel_color(0, 0)
        self.assertIsNotNone(color)
        self.assertEqual(len(color), 3)
        self.assertTrue(0 <= color[0] <= 255)
        self.assertTrue(0 <= color[1] <= 255)
        self.assertTrue(0 <= color[2] <= 255)

    def test_get_pixel_area(self):
        # 测试获取5x5区域
        area = cursor_func.get_pixel_area(100, 100, size=2)
        self.assertEqual(len(area), 5)  # 2*2+1
        self.assertEqual(len(area[0]), 5)
        self.assertEqual(len(area[0][0]), 3)

@unittest.skipUnless(PYD_AVAILABLE, "需要编译后的.pyd模块")
class TestWindowFunc(unittest.TestCase):
    def test_get_screen_resolution(self):
        res = window_func.get_screen_resolution()
        self.assertIsNotNone(res)
        self.assertEqual(len(res), 2)
        self.assertGreater(res[0], 0)
        self.assertGreater(res[1], 0)

    def test_get_foreground_window(self):
        hwnd = window_func.get_foreground_window()
        self.assertIsNotNone(hwnd)
        self.assertGreater(hwnd, 0)

    def test_get_window_info(self):
        hwnd = window_func.get_foreground_window()
        info = window_func.get_window_info(hwnd)
        self.assertIsNotNone(info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertGreater(info['width'], 0)
        self.assertGreater(info['height'], 0)

    def test_find_window_by_name(self):
        # 测试查找计算器窗口(如果存在)
        hwnd = window_func.find_window_by_name(window_name="计算器")
        if hwnd is not None:
            self.assertGreater(hwnd, 0)

if __name__ == '__main__':
    unittest.main()
