# cursor-inspector
一个界面化的鼠标位置查看工具，用于查看鼠标所处位置的像素属性及坐标等数据。为自动化脚本编写提供参考。并且允许选择窗口，以直接查看指定点在窗口内的坐标，包括百分比。

# 编译cython
项目使用cython加速核心函数
```cmd
python setup.py build_ext
```
