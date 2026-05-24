import tkinter as tk
from tkinter import ttk
from src.formula_parser import FormulaParser


class FormulaPanel:
    """公式计算配置面板"""

    def __init__(self, parent, engine, sheet_combo):
        self.engine = engine
        self.sheet_combo = sheet_combo
        self.parser = FormulaParser()

        self.frame = ttk.Frame(parent, padding=5)

        ttk.Label(self.frame, text="公式:").pack(side=tk.LEFT, padx=3)
        self.formula_entry = ttk.Entry(self.frame, width=30)
        self.formula_entry.pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="新列名:").pack(side=tk.LEFT, padx=3)
        self.new_col_entry = ttk.Entry(self.frame, width=12)
        self.new_col_entry.pack(side=tk.LEFT, padx=3)

        ttk.Label(self.frame, text="示例: =销售数量*单价 或 =IF(库存<100,\"需补货\",\"正常\")").pack(side=tk.LEFT, padx=10)

    def execute(self):
        sheet = self.sheet_combo.get()
        formula = self.formula_entry.get().strip()
        new_col = self.new_col_entry.get().strip()

        if not formula:
            raise ValueError("请输入公式")
        if not new_col:
            raise ValueError("请输入新列名")

        df = self.engine.get_sheet_data(sheet)
        result_series = self.parser.evaluate(formula, df)
        df[new_col] = result_series
        return df

    def get_config(self):
        return {
            "formula": self.formula_entry.get(),
            "new_column": self.new_col_entry.get(),
        }

    def set_config(self, config):
        self.formula_entry.delete(0, tk.END)
        self.formula_entry.insert(0, config.get("formula", ""))
        self.new_col_entry.delete(0, tk.END)
        self.new_col_entry.insert(0, config.get("new_column", ""))