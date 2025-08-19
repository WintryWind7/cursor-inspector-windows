import os
import glob
from setuptools import setup, Extension
from Cython.Build import cythonize
from Cython.Compiler import Options

# 配置Cython
Options.build_dir = "core/build"  # 临时文件存放目录
Options.cache_builtins = True

# Windows SDK库配置
libraries = ['user32', 'gdi32', 'psapi']
extra_compile_args = ['/O2']

# 自动发现所有.pyx文件
pyx_files = glob.glob('core/src/*.pyx')
extensions = [
    Extension(
        os.path.splitext(os.path.basename(pyx))[0],
        sources=[pyx],
        libraries=libraries,
        extra_compile_args=extra_compile_args
    )
    for pyx in pyx_files
]

# 自定义构建命令
from setuptools.command.build_ext import build_ext
from distutils.command.clean import clean as _clean

class CustomClean(_clean):
    def run(self):
        # 先执行默认清理
        _clean.run(self)
        # 删除所有临时目录和文件
        dirs_to_remove = ["core/build", "build"]
        files_to_remove = glob.glob("*.pyd")
        
        import shutil
        for dir_path in dirs_to_remove:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"成功删除目录: {dir_path}")
                except Exception as e:
                    print(f"删除目录 {dir_path} 失败: {str(e)}")
        
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"成功删除文件: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 失败: {str(e)}")

class CustomBuildExt(build_ext):
    def build_extension(self, ext):
        # 确保输出目录存在
        os.makedirs("core/dist", exist_ok=True)
        # 修改输出路径到core/dist
        ext._file_path = os.path.join("core/dist", 
                                    self.get_ext_filename(ext.name))
        super().build_extension(ext)

setup(
    name="cursor_inspector",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'embedsignature': True
        },
        build_dir="core/build"  # 临时文件存放目录
    ),
    cmdclass={
        'build_ext': CustomBuildExt,
        'clean': CustomClean
    },
    script_args=['build_ext'],  # 默认运行build_ext!!
    options={
        'build': {
            'build_base': 'core/build'  # 控制build目录位置
        },
        'build_ext': {
            'inplace': False,  # 禁用inplace构建
            'build_lib': 'core/dist'  # 指定输出目录
        }
    },
    # 清理选项
    clean_options = {
        'clean': {
            'build_base': 'core/build'
        }
    }
)
