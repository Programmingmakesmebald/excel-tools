import tkinter as tk
from tkinter import ttk


class MergePanel:
    """表合并/拼接配置面板"""

    MODES = ["上下拼接", "左右扩展"]
    MODE_MAP = {"上下拼接": "vertical", "左右扩展": "horizontal"}

    def __init__(self, parent, engine, sheet_combo):
        self.engine = engine
        self.sheet_combo = sheet_combo

        self.frame = ttk.Frame(parent, padding=5)

        ttk.Label(self.frame, text="模式:").pack(side=tk.LEFT, padx=3)
        self.mode_combo = ttk.Combobox(self.frame, values=self.MODES, state="readonly", width=10)
        self.mode_combo.pack(side=tk.LEFT, padx=3)
        self.mode_combo.set("上下拼接")

        ttk.Label(self.frame, text="Sheet 1:").pack(side=tk.LEFT, padx=3)
        self.sheet1 = ttk.Combobox(self.frame, state="readonly", width=10)
        self.sheet1.pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="Sheet 2:").pack(side=tk.LEFT, padx=3)
        self.sheet2 = ttk.Combobox(self.frame, state="readonly", width=10)
        self.sheet2.pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="匹配列:").pack(side=tk.LEFT, padx=3)
        self.match_col = ttk.Combobox(self.frame, state="readonly", width=10)
        self.match_col.pack(side=tk.LEFT, padx=3)

        self.sheet_combo.bind("<<ComboboxSelected>>", self._update_sheets)

    def _update_sheets(self, event=None):
        sheets = list(self.sheet_combo["values"]) if self.sheet_combo["values"] else []
        self.sheet1["values"] = sheets
        self.sheet2["values"] = sheets
        self.sheet1.set(self.sheet_combo.get())
        self.sheet2.set(sheets[1] if len(sheets) > 1 else "")
        # 更新匹配列
        sheet = self.sheet_combo.get()
        if sheet:
            try:
                cols = self.engine.get_columns(sheet)
                self.match_col["values"] = cols
            except ValueError:
                self.match_col["values"] = []

    def execute(self):
        mode = self.MODE_MAP[self.mode_combo.get()]
        sheet1_name = self.sheet1.get()
        sheet2_name = self.sheet2.get()
        match_col = self.match_col.get() if mode == "horizontal" else self.match_col.get() or None
        return self.engine.merge_sheets(
            sheet_names=[sheet1_name, sheet2_name],
            mode=mode,
            match_column=match_col
        )

    def get_config(self):
        return {
            "mode": self.MODE_MAP[self.mode_combo.get()],
            "sheet1": self.sheet1.get(),
            "sheet2": self.sheet2.get(),
            "match_column": self.match_col.get(),
        }

    def set_config(self, config):
        mode = config.get("mode", "vertical")
        display = next((k for k, v in self.MODE_MAP.items() if v == mode), "上下拼接")
        self.mode_combo.set(display)
        self.sheet1.set(config.get("sheet1", ""))
        self.sheet2.set(config.get("sheet2", ""))
        self.match_col.set(config.get("match_column", ""))