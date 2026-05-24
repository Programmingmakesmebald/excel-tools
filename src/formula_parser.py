import re
import pandas as pd
import numpy as np


class FormulaParser:
    """解析 Excel 风格公式，转换为 pandas 向量化操作"""

    IF_PATTERN = re.compile(
        r'^IF\((.+?),\s*(.+?),\s*(.+?)\)$',
        re.IGNORECASE
    )

    COLUMN_PATTERN = re.compile(r'[A-Za-z_一-鿿][A-Za-z0-9_一-鿿]*')

    LETTER_COL_PATTERN = re.compile(r'^[A-Z]$')

    def evaluate(self, formula: str, df: pd.DataFrame) -> pd.Series:
        """解析公式并在 DataFrame 上执行，返回新的 Series"""
        expr = formula.strip()
        if expr.startswith("="):
            expr = expr[1:]

        if_match = self.IF_PATTERN.match(expr)
        if if_match:
            return self._eval_if(if_match.group(1), if_match.group(2),
                                  if_match.group(3), df)

        try:
            return self._eval_arithmetic(expr, df)
        except Exception as e:
            raise ValueError(f"公式语法错误: {e}")

    def _resolve_column(self, name: str, df: pd.DataFrame) -> pd.Series:
        """将列名（中文或字母）映射到 DataFrame 的列"""
        name = name.strip()
        if self.LETTER_COL_PATTERN.match(name):
            idx = ord(name) - ord('A')
            if idx < len(df.columns):
                return df.iloc[:, idx]
            raise ValueError(f"列引用 '{name}' 超出范围（共 {len(df.columns)} 列）")

        if name in df.columns:
            return df[name]

        raise ValueError(f"未找到列 '{name}'")

    def _replace_columns_in_expr(self, expr: str, df: pd.DataFrame) -> tuple[str, dict]:
        """将表达式中的列名替换为变量引用，同时构建变量字典"""
        tokens = self.COLUMN_PATTERN.findall(expr)
        tokens.sort(key=len, reverse=True)

        variables = {}
        result = expr
        for token in tokens:
            if token.upper() in ("IF", "AND", "OR", "NOT"):
                continue
            try:
                series = self._resolve_column(token, df)
                var_name = f"col_{token}"
                variables[var_name] = series
                result = result.replace(token, var_name)
            except ValueError:
                pass

        return result, variables

    def _eval_arithmetic(self, expr: str, df: pd.DataFrame) -> pd.Series:
        """评估算术表达式"""
        replaced_expr, variables = self._replace_columns_in_expr(expr, df)

        if not variables:
            raise ValueError("公式中没有有效的列引用")

        result = pd.eval(replaced_expr, local_dict=variables)
        return result

    def _eval_if(self, condition: str, true_val: str,
                 false_val: str, df: pd.DataFrame) -> pd.Series:
        """评估 IF(condition, true_value, false_value)"""
        cond_expr, cond_vars = self._replace_columns_in_expr(condition, df)

        if not cond_vars:
            raise ValueError(f"IF 条件中没有有效的列引用: {condition}")

        cond_result = pd.eval(cond_expr, local_dict=cond_vars)

        true_series = self._parse_value(true_val.strip(), df)
        false_series = self._parse_value(false_val.strip(), df)

        return np.where(cond_result, true_series, false_series)

    def _parse_value(self, val: str, df: pd.DataFrame):
        """解析 IF 的值参数：可能是列引用、字符串、或数字"""
        if (val.startswith('"') and val.endswith('"')) or \
           (val.startswith("'") and val.endswith("'")):
            return val[1:-1]

        try:
            return self._resolve_column(val, df)
        except ValueError:
            pass

        try:
            return float(val) if '.' in val else int(val)
        except ValueError:
            pass

        replaced, variables = self._replace_columns_in_expr(val, df)
        if variables:
            return pd.eval(replaced, local_dict=variables)

        raise ValueError(f"无法解析值: {val}")