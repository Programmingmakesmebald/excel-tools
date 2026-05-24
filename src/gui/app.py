import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
from src.excel_engine import ExcelEngine
from src.config_manager import ConfigManager
from src.gui.match_panel import MatchPanel
from src.gui.filter_panel import FilterPanel
from src.gui.group_panel import GroupPanel
from src.gui.merge_panel import MergePanel
from src.gui.formula_panel import FormulaPanel


class ExcelApp:
    """主窗口：上下分区布局"""

    OPERATIONS = ["多表匹配", "筛选/去重/排序", "分组汇总", "表合并/拼接", "公式计算"]

    def __init__(self):
        self.engine = ExcelEngine()
        self.config_mgr = ConfigManager()
        self._result_df = None

        self.root = tk.Tk()
        self.root.title("Excel 进销存处理工具")
        self.root.geometry("950x650")
        self.root.minsize(800, 500)

        self._build_toolbar()
        self._build_param_area()
        self._build_preview_area()
        self._build_status_bar()

    def _build_toolbar(self):
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(toolbar, text="打开文件", command=self._on_open_file).pack(side=tk.LEFT, padx=3)

        self.file_label = ttk.Label(toolbar, text="未打开文件")
        self.file_label.pack(side=tk.LEFT, padx=10)

        ttk.Label(toolbar, text="Sheet:").pack(side=tk.LEFT, padx=3)
        self.sheet_combo = ttk.Combobox(toolbar, state="readonly", width=12)
        self.sheet_combo.pack(side=tk.LEFT, padx=3)

        ttk.Label(toolbar, text="操作:").pack(side=tk.LEFT, padx=3)
        self.op_combo = ttk.Combobox(toolbar, values=self.OPERATIONS, state="readonly", width=14)
        self.op_combo.pack(side=tk.LEFT, padx=3)
        self.op_combo.bind("<<ComboboxSelected>>", self._on_operation_change)

        ttk.Button(toolbar, text="执行", command=self._on_execute).pack(side=tk.LEFT, padx=10)

        ttk.Button(toolbar, text="保存配置", command=self._on_save_config).pack(side=tk.RIGHT, padx=3)
        ttk.Button(toolbar, text="加载配置", command=self._on_load_config).pack(side=tk.RIGHT, padx=3)

    def _build_param_area(self):
        self.param_frame = ttk.Frame(self.root, padding=5)
        self.param_frame.pack(fill=tk.X, side=tk.TOP)

        self.panels = {
            "多表匹配": MatchPanel(self.param_frame, self.engine, self.sheet_combo),
            "筛选/去重/排序": FilterPanel(self.param_frame, self.engine, self.sheet_combo),
            "分组汇总": GroupPanel(self.param_frame, self.engine, self.sheet_combo),
            "表合并/拼接": MergePanel(self.param_frame, self.engine, self.sheet_combo),
            "公式计算": FormulaPanel(self.param_frame, self.engine, self.sheet_combo),
        }
        self._current_panel = None

    def _build_preview_area(self):
        preview_frame = ttk.Frame(self.root, padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        ttk.Label(preview_frame, text="结果预览（前5行）").pack(anchor=tk.W)

        self.tree = ttk.Treeview(preview_frame, show="headings", height=6)
        self.tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(preview_frame, text="保存为新 Excel 文件",
                   command=self._on_save_file).pack(anchor=tk.W, pady=5)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)

    def _on_open_file(self):
        path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            names = self.engine.load_file(path)
            self.sheet_combo["values"] = names
            self.sheet_combo.set(names[0] if names else "")
            self.file_label.config(text=path.split("/")[-1].split("\\")[-1])
            self.status_var.set(f"已加载: {len(names)} 个 sheet")
        except FileNotFoundError as e:
            messagebox.showerror("错误", str(e))

    def _on_operation_change(self, event=None):
        op = self.op_combo.get()
        if self._current_panel:
            self._current_panel.frame.pack_forget()
        panel = self.panels[op]
        panel.frame.pack(fill=tk.X)
        self._current_panel = panel

    def _on_execute(self):
        op = self.op_combo.get()
        if not op or not self._current_panel:
            messagebox.showwarning("提示", "请先选择操作类型")
            return
        try:
            self._result_df = self._current_panel.execute()
            self._show_preview(self._result_df)
            self.status_var.set(f"执行完成: {len(self._result_df)} 行")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _on_save_file(self):
        if self._result_df is None:
            messagebox.showwarning("提示", "请先执行操作")
            return
        path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")]
        )
        if not path:
            return
        try:
            self.engine.save_to_file(self._result_df, path)
            self.status_var.set(f"已保存: {path}")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))

    def _on_save_config(self):
        if not self._current_panel:
            messagebox.showwarning("提示", "请先选择操作类型")
            return
        name = simpledialog.askstring("保存配置", "配置名称:", parent=self.root)
        if not name:
            return
        config = self._current_panel.get_config()
        config["operation"] = self.op_combo.get()
        self.config_mgr.save_config(name, config)
        self.status_var.set(f"配置已保存: {name}")

    def _on_load_config(self):
        configs = self.config_mgr.list_configs()
        if not configs:
            messagebox.showinfo("提示", "没有已保存的配置")
            return
        name = simpledialog.askstring("加载配置", "配置名称:\n可选: " + ", ".join(configs), parent=self.root)
        if not name:
            return
        try:
            config = self.config_mgr.load_config(name)
            op = config["operation"]
            self.op_combo.set(op)
            self._on_operation_change()
            self._current_panel.set_config(config)
            self.status_var.set(f"配置已加载: {name}")
        except FileNotFoundError:
            messagebox.showerror("错误", "未找到该配置")

    def _show_preview(self, df: pd.DataFrame):
        self.tree.delete(*self.tree.get_children())
        preview = df.head(5)
        cols = list(preview.columns)
        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        for _, row in preview.iterrows():
            values = [str(v) if pd.notna(v) else "" for v in row]
            self.tree.insert("", tk.END, values=values)

    def run(self):
        self.root.mainloop()