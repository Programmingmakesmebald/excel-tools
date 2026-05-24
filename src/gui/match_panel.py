import tkinter as tk
from tkinter import ttk


class MatchPanel:
    """多表匹配配置面板：基础表 + 多条匹配规则"""

    JOIN_TYPES = ["left（左连接）", "inner（内连接）", "outer（全连接）"]

    def __init__(self, parent, engine, sheet_combo):
        self.engine = engine
        self.sheet_combo = sheet_combo

        self.frame = ttk.Frame(parent, padding=5)

        ttk.Label(self.frame, text="基础表:").pack(side=tk.LEFT, padx=3)

        self.rules_frame = ttk.Frame(self.frame)
        self.rules_frame.pack(fill=tk.X, pady=5)

        self.rules = []

        ttk.Button(self.frame, text="添加匹配规则",
                   command=self._add_rule_row).pack(anchor=tk.W)

        self._add_rule_row()

    def _add_rule_row(self):
        row_frame = ttk.Frame(self.rules_frame)
        row_frame.pack(fill=tk.X, pady=2)

        idx = len(self.rules)

        ttk.Label(row_frame, text=f"匹配{idx + 1}:").pack(side=tk.LEFT, padx=3)

        target_combo = ttk.Combobox(row_frame, state="readonly", width=10)
        target_combo.pack(side=tk.LEFT, padx=3)
        sheets = list(self.sheet_combo["values"]) if self.sheet_combo["values"] else []
        target_combo["values"] = sheets

        ttk.Label(row_frame, text="匹配列:").pack(side=tk.LEFT, padx=3)
        match_combo = ttk.Combobox(row_frame, state="readonly", width=10)
        match_combo.pack(side=tk.LEFT, padx=3)

        ttk.Label(row_frame, text="带出列:").pack(side=tk.LEFT, padx=3)
        bring_entry = ttk.Entry(row_frame, width=15)
        bring_entry.pack(side=tk.LEFT, padx=3)

        join_combo = ttk.Combobox(row_frame, values=self.JOIN_TYPES, state="readonly", width=14)
        join_combo.pack(side=tk.LEFT, padx=3)
        join_combo.set(self.JOIN_TYPES[0])

        ttk.Button(row_frame, text="删除",
                   command=lambda: self._remove_rule(row_frame, idx)).pack(side=tk.LEFT, padx=3)

        target_combo.bind("<<ComboboxSelected>>",
                          lambda e: self._update_match_columns(target_combo, match_combo))

        self.rules.append({
            "frame": row_frame,
            "target_combo": target_combo,
            "match_combo": match_combo,
            "bring_entry": bring_entry,
            "join_combo": join_combo,
        })

    def _remove_rule(self, frame, idx):
        if len(self.rules) <= 1:
            return
        frame.destroy()
        self.rules[idx] = None

    def _update_match_columns(self, target_combo, match_combo):
        target = target_combo.get()
        if not target:
            return
        try:
            cols = self.engine.get_columns(target)
            match_combo["values"] = cols
        except ValueError:
            match_combo["values"] = []

    def execute(self):
        base_sheet = self.sheet_combo.get()
        rules_config = []
        for rule in self.rules:
            if rule is None:
                continue
            target = rule["target_combo"].get()
            match_col = rule["match_combo"].get()
            bring_str = rule["bring_entry"].get().strip()
            bring_cols = [c.strip() for c in bring_str.split(",") if c.strip()] if bring_str else []
            how_raw = rule["join_combo"].get()
            how = how_raw.split("（")[0] if "（" in how_raw else how_raw

            if not target or not match_col:
                raise ValueError("请完整填写匹配规则（目标sheet和匹配列不能为空）")

            rules_config.append({
                "target_sheet": target,
                "match_column": match_col,
                "bring_columns": bring_cols,
                "how": how,
            })

        return self.engine.multi_match(base_sheet, rules_config)

    def get_config(self):
        rules_config = []
        for rule in self.rules:
            if rule is None:
                continue
            how_raw = rule["join_combo"].get()
            how = how_raw.split("（")[0] if "（" in how_raw else how_raw
            rules_config.append({
                "target_sheet": rule["target_combo"].get(),
                "match_column": rule["match_combo"].get(),
                "bring_columns": rule["bring_entry"].get().split(","),
                "how": how,
            })
        return {"base_sheet": self.sheet_combo.get(), "rules": rules_config}

    def set_config(self, config):
        for rule in self.rules:
            if rule is not None:
                rule["frame"].destroy()
        self.rules = []

        for rule_cfg in config.get("rules", []):
            self._add_rule_row()
            rule = self.rules[-1]
            rule["target_combo"].set(rule_cfg.get("target_sheet", ""))
            rule["match_combo"].set(rule_cfg.get("match_column", ""))
            rule["bring_entry"].delete(0, tk.END)
            rule["bring_entry"].insert(0, ",".join(rule_cfg.get("bring_columns", [])))
            how = rule_cfg.get("how", "left")
            display = f"{how}（{'左' if how == 'left' else '内' if how == 'inner' else '全'}连接）"
            rule["join_combo"].set(display)