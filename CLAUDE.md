# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_excel_engine.py -v

# Run a single test by name
python -m pytest tests/test_excel_engine.py::TestExcelEngineMultiMatch::test_multi_match_chained -v

# Run the GUI app
python src/main.py

# Build standalone executable (generates dist/ExcelInventoryTool.exe on Windows, dist/ExcelInventoryTool.app on Mac)
python build.py

# Install dependencies
pip install pandas openpyxl pyinstaller pytest
```

## Architecture

Three-layer architecture: **data engine → operation panels → GUI app**

- **ExcelEngine** (`src/excel_engine.py`) — core pandas-based data processing. Holds all loaded sheets as `{name: DataFrame}` in memory. All operations (multi_match, filter, dedup, sort, group, merge) are methods on this single class. Every method returns a new DataFrame; the original is never modified.

- **FormulaParser** (`src/formula_parser.py`) — parses Excel-style formulas (e.g. `=销售数量*单价`, `=IF(库存<100,"需补货","正常")`) into pandas vectorized operations. Uses regex token extraction → `pd.eval()` for arithmetic, `np.where()` for IF.

- **ConfigManager** (`src/config_manager.py`) — JSON-based config persistence in `~/.excel_tools_configs/`. Each config stores operation type and panel parameters.

- **GUI panels** (`src/gui/`) — each operation has its own panel class (MatchPanel, FilterPanel, GroupPanel, MergePanel, FormulaPanel). Panels are instantiated once and swapped via `pack/pack_forget`. Each panel has `execute()`, `get_config()`, and `set_config()` methods. The app wires panel `execute()` results into a shared `_result_df` for preview and save.

- **ExcelApp** (`src/gui/app.py`) — top-bottom layout: toolbar (file open, sheet select, op select, execute, config save/load) → parameter panel → preview (Treeview) → status bar. Uses messagebox for errors, simpledialog for config name input.

- **main.py** — entry point with `sys.path.insert(0, project_root)` before imports to resolve the `src` package for both direct run and PyInstaller打包.

## Key Design Decisions

- PyInstaller binary name is English (`ExcelInventoryTool`) — Chinese filenames corrupt in GitHub release assets. The CI workflow renames files to Chinese names after build.
- Mac `.app` is a directory, so CI zips it before upload (otherwise release action can't handle it).
- `conftest.py` teardown uses `try/except PermissionError` on `os.unlink` — Windows locks open Excel files.
- Formula parser sorts column tokens by length (reverse) before replacement to prevent shorter names shadowing longer ones.