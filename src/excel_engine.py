import pandas as pd


class ExcelEngine:
    """数据引擎层：负责 Excel 读写和所有 pandas 数据处理操作"""

    def __init__(self):
        self._file_path = None
        self._sheets = {}  # {sheet_name: DataFrame}

    def load_file(self, path: str) -> list[str]:
        """读取 Excel 文件，返回所有 sheet 名称"""
        try:
            xls = pd.ExcelFile(path, engine="openpyxl")
        except Exception as e:
            raise FileNotFoundError(f"无法打开文件: {e}")

        self._file_path = path
        self._sheets = {}
        for name in xls.sheet_names:
            self._sheets[name] = pd.read_excel(xls, sheet_name=name)

        return xls.sheet_names

    def get_columns(self, sheet_name: str) -> list[str]:
        """返回指定 sheet 的所有列名"""
        if sheet_name not in self._sheets:
            raise ValueError(f"未找到 sheet: {sheet_name}")
        return list(self._sheets[sheet_name].columns)

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """返回指定 sheet 的 DataFrame"""
        if sheet_name not in self._sheets:
            raise ValueError(f"未找到 sheet: {sheet_name}")
        return self._sheets[sheet_name].copy()

    def save_to_file(self, df: pd.DataFrame, output_path: str) -> None:
        """将 DataFrame 保存为新的 Excel 文件"""
        df.to_excel(output_path, index=False, engine="openpyxl")

    def multi_match(self, base_sheet: str, rules: list[dict]) -> pd.DataFrame:
        """多表匹配：基础表依次匹配多个sheet，每次带出新列"""
        if base_sheet not in self._sheets:
            raise ValueError(f"未找到 sheet: {base_sheet}")

        result = self._sheets[base_sheet].copy()

        for rule in rules:
            target = rule["target_sheet"]
            match_col = rule["match_column"]
            bring_cols = rule["bring_columns"]
            how = rule["how"]

            if target not in self._sheets:
                raise ValueError(f"未找到 sheet: {target}")

            right_df = self._sheets[target]
            if match_col not in right_df.columns:
                raise ValueError(f"未找到列 '{match_col}' 在 sheet '{target}' 中")

            right_subset = right_df[[match_col] + bring_cols].copy()
            right_subset = right_subset.drop_duplicates(subset=[match_col])

            result = result.merge(right_subset, on=match_col, how=how)

        if len(result) == 0:
            raise ValueError("匹配结果为空，请检查匹配列")

        return result

    def filter_data(self, sheet_name: str, column: str, op: str, value) -> pd.DataFrame:
        """按列值筛选数据"""
        df = self.get_sheet_data(sheet_name)
        if column not in df.columns:
            raise ValueError(f"未找到列 '{column}' 在 sheet '{sheet_name}' 中")

        col = df[column]
        if op == "equals":
            return df[col == value]
        elif op == "not_equals":
            return df[col != value]
        elif op == "contains":
            return df[col.astype(str).str.contains(str(value), na=False)]
        elif op == "greater_than":
            return df[col > value]
        elif op == "less_than":
            return df[col < value]
        elif op == "starts_with":
            return df[col.astype(str).str.startswith(str(value), na=False)]
        elif op == "ends_with":
            return df[col.astype(str).str.endswith(str(value), na=False)]
        else:
            raise ValueError(f"不支持的操作类型: {op}")

    def dedup_data(self, sheet_name: str, columns: list[str], keep: str = "first") -> pd.DataFrame:
        """按指定列去重"""
        df = self.get_sheet_data(sheet_name)
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"未找到列 '{col}' 在 sheet '{sheet_name}' 中")
        return df.drop_duplicates(subset=columns, keep=keep)

    def sort_data(self, sheet_name: str, columns: list[str], ascending: list[bool] = None) -> pd.DataFrame:
        """按指定列排序"""
        df = self.get_sheet_data(sheet_name)
        if ascending is None:
            ascending = [True] * len(columns)
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"未找到列 '{col}' 在 sheet '{sheet_name}' 中")
        return df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)

    def group_data(self, sheet_name: str, group_columns: list[str],
                   agg_column: str, agg_func: str) -> pd.DataFrame:
        """分组汇总"""
        df = self.get_sheet_data(sheet_name)
        for col in group_columns:
            if col not in df.columns:
                raise ValueError(f"未找到列 '{col}' 在 sheet '{sheet_name}' 中")
        if agg_column not in df.columns:
            raise ValueError(f"未找到列 '{agg_column}' 在 sheet '{sheet_name}' 中")

        valid_funcs = {"sum", "count", "mean", "max", "min"}
        if agg_func not in valid_funcs:
            raise ValueError(f"不支持的汇总方式: {agg_func}")

        grouped = df.groupby(group_columns, observed=True)[agg_column].agg(agg_func).reset_index()
        grouped.columns = group_columns + [agg_column]
        return grouped

    def merge_sheets(self, sheet_names: list[str], mode: str,
                     match_column: str = None) -> pd.DataFrame:
        """表合并/拼接"""
        dfs = []
        for name in sheet_names:
            if name not in self._sheets:
                raise ValueError(f"未找到 sheet: {name}")
            dfs.append(self._sheets[name].copy())

        if mode == "vertical":
            common_cols = list(set.intersection(*[set(df.columns) for df in dfs]))
            aligned = [df[common_cols] for df in dfs]
            result = pd.concat(aligned, ignore_index=True)
            if match_column:
                result = result.drop_duplicates(subset=[match_column], keep="first")
            return result

        elif mode == "horizontal":
            if not match_column:
                raise ValueError("左右扩展模式必须指定匹配列")
            result = dfs[0]
            for df in dfs[1:]:
                if match_column not in df.columns:
                    raise ValueError(f"未找到匹配列 '{match_column}'")
                subset = df.drop_duplicates(subset=[match_column])
                result = result.merge(subset, on=match_column, how="outer")
            return result

        else:
            raise ValueError(f"不支持的模式: {mode}")