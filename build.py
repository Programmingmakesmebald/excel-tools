"""PyInstaller 打包脚本

Windows: python build.py → 生成 dist/ExcelInventoryTool.exe
Mac: python build.py → 生成 dist/ExcelInventoryTool.app
"""
import PyInstaller.__main__
import sys
import os


def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, "src")

    add_data_sep = ";" if sys.platform == "win32" else ":"

    args = [
        os.path.join(src_dir, "main.py"),
        "--name=ExcelInventoryTool",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data=" + src_dir + add_data_sep + "src",
    ]

    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()