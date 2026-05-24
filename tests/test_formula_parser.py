import pytest
import pandas as pd
from src.formula_parser import FormulaParser


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "销售数量": [10, 20, 30],
        "单价": [100, 200, 150],
        "成本": [60, 100, 80],
        "库存": [50, 15, 80],
    })


@pytest.fixture
def parser():
    return FormulaParser()


class TestFormulaArithmetic:
    def test_multiply_columns(self, parser, sample_df):
        result = parser.evaluate("=销售数量*单价", sample_df)
        assert list(result) == [1000, 4000, 4500]

    def test_subtract_columns(self, parser, sample_df):
        result = parser.evaluate("=单价-成本", sample_df)
        assert list(result) == [40, 100, 70]

    def test_complex_arithmetic(self, parser, sample_df):
        result = parser.evaluate("=(单价-成本)*销售数量", sample_df)
        assert list(result) == [400, 2000, 2100]


class TestFormulaIF:
    def test_if_condition(self, parser, sample_df):
        result = parser.evaluate('=IF(库存<50,"需补货","正常")', sample_df)
        assert list(result) == ["正常", "需补货", "正常"]

    def test_if_with_number_result(self, parser, sample_df):
        result = parser.evaluate("=IF(销售数量>15,单价,成本)", sample_df)
        assert list(result) == [60, 200, 150]


class TestFormulaExcelColumnRef:
    def test_letter_column_ref(self, parser, sample_df):
        # A = 第1列 = 销售数量, B = 第2列 = 单价
        result = parser.evaluate("=A*B", sample_df)
        assert list(result) == [1000, 4000, 4500]


class TestFormulaError:
    def test_unknown_column_raises(self, parser, sample_df):
        with pytest.raises(ValueError, match="公式语法错误"):
            parser.evaluate("=不存在的列*单价", sample_df)

    def test_syntax_error_raises(self, parser, sample_df):
        with pytest.raises(ValueError, match="公式语法错误"):
            parser.evaluate("=+*单价", sample_df)