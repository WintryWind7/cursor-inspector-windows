# Cursor Inspector (鼠标检查器)

一个界面化的鼠标位置查看工具，用于查看鼠标所处位置的像素属性及坐标等数据。为自动化脚本编写提供参考。并且允许选择窗口，以直接查看指定点在窗口内的坐标，包括百分比。

## 功能特性

- 🖱️ **实时鼠标位置监控** - 显示鼠标在屏幕上的精确坐标
- 🎨 **像素颜色获取** - 获取鼠标位置的像素颜色值 (RGB/HEX)
- 🪟 **窗口选择功能** - 选择特定窗口并显示鼠标在窗口内的相对位置
- 📊 **百分比坐标** - 显示鼠标在选定窗口内的百分比位置（精确到小数点后4位）
- ⚡ **高性能** - 使用 Cython 优化的核心函数，确保流畅的实时更新
- 🔄 **自动更新** - 使用 Windows API 钩子自动监测窗口位置变化

## 快速开始

### 方式一：直接运行可执行文件（推荐）

1. 从 [Releases](../../releases) 页面下载最新版本
2. 解压到任意目录
3. 双击 `cursor-inspector.exe` 或运行 `run.bat`

### 方式二：从源码构建

#### 环境要求

- Python 3.8+
- Windows 操作系统
- Visual Studio Build Tools (用于编译 Cython)

#### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/your-username/cursor-inspector-windows.git
cd cursor-inspector-windows
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 构建 Cython 模块：
```bash
python setup.py build_ext
```

5. 运行程序：
```bash
python main.py
```

#### 构建可执行文件

如果你想要构建自己的可执行文件：

```bash
# 方式一：使用批处理文件（推荐）
build.bat

# 方式二：手动构建
python build_exe.py
```

构建完成后，可执行文件将位于 `dist/cursor-inspector.exe`。

## 使用说明

1. **启动程序** - 运行程序后会显示实时的鼠标位置和像素颜色
2. **选择窗口** - 从下拉菜单中选择要监控的窗口
3. **查看信息** - 程序会显示：
   - 系统信息：桌面分辨率、鼠标位置、像素颜色
   - 窗口信息：窗口位置、鼠标在窗口内的位置和百分比

## 技术架构

- **GUI框架**: PySide6 (Qt6)
- **核心模块**: Cython 优化的 Windows API 调用
- **系统集成**: Windows API 钩子实现实时监控
- **打包工具**: PyInstaller

## 开发

### 项目结构

```
cursor-inspector-windows/
├── core/
│   └── src/
│       ├── cursor_func.pyx    # 鼠标和像素相关函数
│       └── window_func.pyx    # 窗口相关函数
├── tests/                     # 单元测试
├── main.py                   # 主程序入口
├── setup.py                  # Cython 构建配置
├── build_exe.py             # 可执行文件构建脚本
└── requirements.txt         # 依赖列表
```

### 编译 Cython 模块

项目使用cython加速核心函数

```bash
python setup.py build_ext
```

### 运行测试

```bash
python -m pytest tests/
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

查看 [Releases](../../releases) 页面了解版本更新信息。
