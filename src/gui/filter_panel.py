import tkinter as tk
from tkinter import ttk


class FilterPanel:
    """筛选/去重/排序配置面板"""

    FILTER_OPS = ["等于", "包含", "大于", "小于", "不等于", "开头是", "结尾是"]
    OP_MAP = {
        "等于": "equals", "包含": "contains", "大于": "greater_than",
        "小于": "less_than", "不等于": "not_equals", "开头是": "starts_with", "结尾是": "ends_with",
    }
    DEDUP_KEEP = ["保留第一条", "保留最后一条"]
    KEEP_MAP = {"保留第一条": "first", "保留最后一条": "last"}
    SORT_DIRS = ["升序", "降序"]

    def __init__(self, parent, engine, sheet_combo):
        self.engine = engine
        self.sheet_combo = sheet_combo

        self.frame = ttk.Frame(parent, padding=5)

        ttk.Label(self.frame, text="子操作:").pack(side=tk.LEFT, padx=3)
        self.sub_op = ttk.Combobox(self.frame,
                                    values=["筛选", "去重", "排序"], state="readonly", width=8)
        self.sub_op.pack(side=tk.LEFT, padx=3)
        self.sub_op.set("筛选")
        self.sub_op.bind("<<ComboboxSelected>>", self._on_sub_op_change)

        # 筛选
        self.filter_frame = ttk.Frame(self.frame)
        ttk.Label(self.filter_frame, text="列:").pack(side=tk.LEFT, padx=2)
        self.filter_col = ttk.Combobox(self.filter_frame, state="readonly", width=10)
        self.filter_col.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.filter_frame, text="条件:").pack(side=tk.LEFT, padx=2)
        self.filter_op = ttk.Combobox(self.filter_frame, values=self.FILTER_OPS, state="readonly", width=8)
        self.filter_op.pack(side=tk.LEFT, padx=2)
        self.filter_op.set("等于")
        ttk.Label(self.filter_frame, text="值:").pack(side=tk.LEFT, padx=2)
        self.filter_val = ttk.Entry(self.filter_frame, width=10)
        self.filter_val.pack(side=tk.LEFT, padx=2)

        # 去重
        self.dedup_frame = ttk.Frame(self.frame)
        ttk.Label(self.dedup_frame, text="列:").pack(side=tk.LEFT, padx=2)
        self.dedup_cols = ttk.Entry(self.dedup_frame, width=15)
        self.dedup_cols.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.dedup_frame, text="(多列逗号分隔)").pack(side=tk.LEFT, padx=2)
        ttk.Label(self.dedup_frame, text="保留:").pack(side=tk.LEFT, padx=2)
        self.dedup_keep = ttk.Combobox(self.dedup_frame, values=self.DEDUP_KEEP, state="readonly", width=10)
        self.dedup_keep.pack(side=tk.LEFT, padx=2)
        self.dedup_keep.set("保留第一条")

        # 排序
        self.sort_frame = ttk.Frame(self.frame)
        ttk.Label(self.sort_frame, text="列:").pack(side=tk.LEFT, padx=2)
        self.sort_cols = ttk.Entry(self.sort_frame, width=15)
        self.sort_cols.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.sort_frame, text="(多列逗号分隔)").pack(side=tk.LEFT, padx=2)
        ttk.Label(self.sort_frame, text="方向:").pack(side=tk.LEFT, padx=2)
        self.sort_dir = ttk.Combobox(self.sort_frame, values=self.SORT_DIRS, state="readonly", width=8)
        self.sort_dir.pack(side=tk.LEFT, padx=2)
        self.sort_dir.set("升序")

        self._on_sub_op_change()
        self.sheet_combo.bind("<<ComboboxSelected>>", self._update_columns)

    def _on_sub_op_change(self, event=None):
        self.filter_frame.pack_forget()
        self.dedup_frame.pack_forget()
        self.sort_frame.pack_forget()
        op = self.sub_op.get()
        if op == "筛选":
            self.filter_frame.pack(side=tk.LEFT, padx=10)
        elif op == "去重":
            self.dedup_frame.pack(side=tk.LEFT, padx=10)
        elif op == "排序":
            self.sort_frame.pack(side=tk.LEFT, padx=10)

    def _update_columns(self, event=None):
        sheet = self.sheet_combo.get()
        if sheet:
            try:
                cols = self.engine.get_columns(sheet)
                self.filter_col["values"] = cols
            except ValueError:
                self.filter_col["values"] = []

    def execute(self):
        sheet = self.sheet_combo.get()
        op = self.sub_op.get()
        if op == "筛选":
            col = self.filter_col.get()
            cond = self.filter_op.get()
            val_str = self.filter_val.get()
            op_key = self.OP_MAP[cond]
            try:
                val = float(val_str) if "." in val_str else int(val_str)
            except ValueError:
                val = val_str
            return self.engine.filter_data(sheet, column=col, op=op_key, value=val)
        elif op == "去重":
            cols = [c.strip() for c in self.dedup_cols.get().split(",") if c.strip()]
            keep = self.KEEP_MAP[self.dedup_keep.get()]
            return self.engine.dedup_data(sheet, columns=cols, keep=keep)
        elif op == "排序":
            cols = [c.strip() for c in self.sort_cols.get().split(",") if c.strip()]
            ascending = [self.sort_dir.get() == "升序"] * len(cols)
            return self.engine.sort_data(sheet, columns=cols, ascending=ascending)

    def get_config(self):
        op = self.sub_op.get()
        config = {"sub_operation": op}
        if op == "筛选":
            config["column"] = self.filter_col.get()
            config["op"] = self.OP_MAP[self.filter_op.get()]
            config["value"] = self.filter_val.get()
        elif op == "去重":
            config["columns"] = self.dedup_cols.get()
            config["keep"] = self.KEEP_MAP[self.dedup_keep.get()]
        elif op == "排序":
            config["columns"] = self.sort_cols.get()
            config["ascending"] = self.sort_dir.get() == "升序"
        return config

    def set_config(self, config):
        self.sub_op.set(config.get("sub_operation", "筛选"))
        self._on_sub_op_change()
        op = config.get("sub_operation", "筛选")
        if op == "筛选":
            self.filter_col.set(config.get("column", ""))
            op_key = config.get("op", "equals")
            display = next((k for k, v in self.OP_MAP.items() if v == op_key), "等于")
            self.filter_op.set(display)
            self.filter_val.delete(0, tk.END)
            self.filter_val.insert(0, config.get("value", ""))
        elif op == "去重":
            self.dedup_cols.delete(0, tk.END)
            self.dedup_cols.insert(0, config.get("columns", ""))
            keep = config.get("keep", "first")
            self.dedup_keep.set("保留第一条" if keep == "first" else "保留最后一条")
        elif op == "排序":
            self.sort_cols.delete(0, tk.END)
            self.sort_cols.insert(0, config.get("columns", ""))
            self.sort_dir.set("升序" if config.get("ascending", True) else "降序")