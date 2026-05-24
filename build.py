"""PyInstaller 打包脚本

Windows: python build.py → 生成 dist/Excel进销存工具.exe
Mac: python build.py → 生成 dist/Excel进销存工具.app
"""
import PyInstaller.__main__
import sys
import os


def build():
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, "src")

    args = [
        os.path.join(src_dir, "main.py"),
        "--name=Excel进销存工具",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data=" + src_dir + ";" + "src" if sys.platform == "win32" else "--add-data=" + src_dir + ":" + "src",
    ]

    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()