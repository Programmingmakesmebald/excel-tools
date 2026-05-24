# Excel进销存处理工具

轻量级跨平台 Excel 进销存数据处理工具，替代 Excel VLOOKUP 等手动操作，支持 10万+ 行数据流畅处理。

## 功能

| 操作 | 说明 |
|------|------|
| 多表匹配 | VLOOKUP 替代，支持跨多表链式匹配，可选 left/inner/outer 连接 |
| 筛选/去重/排序 | 按列值筛选、去重、升降序排序 |
| 分组汇总 | 按列分组并求和/计数/均值/最大/最小 |
| 表合并/拼接 | 纵向拼接多表、横向按匹配列扩展 |
| 公式计算 | Excel 风格公式，如 `=销售数量*单价`、`=IF(库存<100,"需补货","正常")` |
| 配置保存 | 保存操作配置，下次直接加载复用 |

## 下载

从 [GitHub Releases](https://github.com/Programmingmakesmebald/excel-tools/releases) 下载：

- **Windows**: `Excel进销存工具-Windows.exe`，双击运行
- **Mac**: `Excel进销存工具-Mac.zip`，解压后打开 .app 文件

无需安装 Python 或任何依赖。

## 使用方式

1. 打开文件 — 选择包含多个 sheet 的 Excel 文件
2. 选择操作 — 从5种操作中选择
3. 配置参数 — 设置匹配规则/筛选条件/公式等
4. 执行 — 结果在下方预览
5. 保存 — 导出为新 Excel 文件（原始文件不会被修改）

## 本地开发

```bash
pip install pandas openpyxl pytest pyinstaller
python -m pytest tests/ -v       # 运行测试
python src/main.py                # 启动 GUI
python build.py                   # 打包可执行文件
```

## 技术栈

- Python 3.12 + pandas + openpyxl
- Tkinter GUI
- PyInstaller 打包
- GitHub Actions 跨平台构建