import tkinter as tk
from tkinter import ttk


class GroupPanel:
    """分组汇总配置面板"""

    AGG_FUNCS = ["求和", "计数", "平均值", "最大值", "最小值"]
    FUNC_MAP = {"求和": "sum", "计数": "count", "平均值": "mean", "最大值": "max", "最小值": "min"}

    def __init__(self, parent, engine, sheet_combo):
        self.engine = engine
        self.sheet_combo = sheet_combo

        self.frame = ttk.Frame(parent, padding=5)

        ttk.Label(self.frame, text="分组列:").pack(side=tk.LEFT, padx=3)
        self.group_cols = ttk.Entry(self.frame, width=15)
        self.group_cols.pack(side=tk.LEFT, padx=3)
        ttk.Label(self.frame, text="(多列逗号分隔)").pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="汇总列:").pack(side=tk.LEFT, padx=3)
        self.agg_col = ttk.Combobox(self.frame, state="readonly", width=10)
        self.agg_col.pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="汇总方式:").pack(side=tk.LEFT, padx=3)
        self.agg_func = ttk.Combobox(self.frame, values=self.AGG_FUNCS, state="readonly", width=8)
        self.agg_func.pack(side=tk.LEFT, padx=3)
        self.agg_func.set("求和")

        self.sheet_combo.bind("<<ComboboxSelected>>", self._update_columns)

    def _update_columns(self, event=None):
        sheet = self.sheet_combo.get()
        if sheet:
            try:
                cols = self.engine.get_columns(sheet)
                self.agg_col["values"] = cols
            except ValueError:
                self.agg_col["values"] = []

    def execute(self):
        sheet = self.sheet_combo.get()
        group_cols = [c.strip() for c in self.group_cols.get().split(",") if c.strip()]
        agg_col = self.agg_col.get()
        func_key = self.FUNC_MAP[self.agg_func.get()]
        return self.engine.group_data(sheet, group_columns=group_cols,
                                       agg_column=agg_col, agg_func=func_key)

    def get_config(self):
        return {
            "group_columns": self.group_cols.get(),
            "agg_column": self.agg_col.get(),
            "agg_func": self.FUNC_MAP[self.agg_func.get()],
        }

    def set_config(self, config):
        self.group_cols.delete(0, tk.END)
        self.group_cols.insert(0, config.get("group_columns", ""))
        self.agg_col.set(config.get("agg_column", ""))
        func = config.get("agg_func", "sum")
        display = next((k for k, v in self.FUNC_MAP.items() if v == func), "求和")
        self.agg_func.set(display)