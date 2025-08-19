from libc.stdint cimport uint32_t
from cpython cimport PyObject, Py_INCREF
import numpy as np

cdef extern from "Windows.h":
    ctypedef struct POINT:
        long x
        long y
    ctypedef void* HWND
    ctypedef unsigned long DWORD
    ctypedef int BOOL
    
    BOOL GetCursorPos(POINT* lpPoint)
    DWORD GetPixel(void* hdc, int x, int y)
    void* GetDC(HWND hWnd)
    int ReleaseDC(HWND hWnd, void* hDC)
    HWND GetDesktopWindow()

def get_cursor_position():
    """获取鼠标当前位置"""
    cdef POINT point
    if GetCursorPos(&point):
        return (point.x, point.y)
    return None

def get_pixel_color(int x, int y):
    """获取屏幕指定位置的像素颜色"""
    cdef HWND hwnd = GetDesktopWindow()
    cdef void* hdc = GetDC(hwnd)
    cdef DWORD color = GetPixel(hdc, x, y)
    ReleaseDC(hwnd, hdc)
    return (color & 0xff, (color >> 8) & 0xff, (color >> 16) & 0xff)

def get_pixel_area(int x, int y, int size=5):
    """获取鼠标周围区域像素(11x11)"""
    cdef HWND hwnd = GetDesktopWindow()
    cdef void* hdc = GetDC(hwnd)
    
    cdef int i, j
    cdef DWORD color
    cdef list area = []
    
    for i in range(-size, size+1):
        row = []
        for j in range(-size, size+1):
            color = GetPixel(hdc, x + j, y + i)
            row.append((color & 0xff, (color >> 8) & 0xff, (color >> 16) & 0xff))
        area.append(row)
    
    ReleaseDC(hwnd, hdc)
    return area
