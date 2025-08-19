import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'dist')))

import cursor_func

class TestCursorFunc(unittest.TestCase):
    def test_get_cursor_position(self):
        """测试获取鼠标位置功能"""
        pos = cursor_func.get_cursor_position()
        self.assertIsNotNone(pos, "获取鼠标位置失败")
        self.assertEqual(len(pos), 2, "鼠标位置应为(x,y)坐标")
        self.assertIsInstance(pos[0], int, "X坐标应为整数")
        self.assertIsInstance(pos[1], int, "Y坐标应为整数")
        
        # 验证坐标值合理性
        screen_width, screen_height = self._get_screen_resolution()
        self.assertTrue(0 <= pos[0] <= screen_width, "X坐标超出屏幕范围")
        self.assertTrue(0 <= pos[1] <= screen_height, "Y坐标超出屏幕范围")

    def test_get_pixel_color(self):
        """测试获取像素颜色功能"""
        # 测试屏幕左上角像素
        color = cursor_func.get_pixel_color(0, 0)
        self.assertIsNotNone(color, "获取像素颜色失败")
        self.assertEqual(len(color), 3, "颜色值应为(R,G,B)三元组")
        
        for channel in color:
            self.assertIsInstance(channel, int, "颜色通道值应为整数")
            self.assertTrue(0 <= channel <= 255, "颜色通道值应在0-255范围内")

    def test_get_pixel_area(self):
        """测试获取像素区域功能"""
        # 测试获取5x5区域(实际获取11x11，因为size=5表示半径)
        area = cursor_func.get_pixel_area(100, 100, size=5)
        self.assertIsNotNone(area, "获取像素区域失败")
        self.assertEqual(len(area), 11, "区域高度应为11像素")
        self.assertEqual(len(area[0]), 11, "区域宽度应为11像素")
        
        # 验证每个像素点的颜色格式
        for row in area:
            for pixel in row:
                self.assertEqual(len(pixel), 3, "每个像素应为(R,G,B)三元组")
                for channel in pixel:
                    self.assertTrue(0 <= channel <= 255, "颜色通道值应在0-255范围内")

    def _get_screen_resolution(self):
        """获取屏幕分辨率"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        except:
            # 默认返回常见分辨率
            return 1920, 1080

if __name__ == "__main__":
    unittest.main()
