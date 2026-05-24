import pytest
from src.excel_engine import ExcelEngine


class TestExcelEngineRead:
    def test_load_file_returns_sheet_names(self, sample_excel_path):
        engine = ExcelEngine()
        sheet_names = engine.load_file(sample_excel_path)
        assert sheet_names == ["采购明细", "销售记录", "库存表", "商品信息"]

    def test_get_columns_returns_column_names(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        cols = engine.get_columns("采购明细")
        assert cols == ["商品编号", "商品名称", "采购数量", "采购单价", "采购日期"]

    def test_get_sheet_data_returns_dataframe(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        df = engine.get_sheet_data("采购明细")
        assert len(df) == 4
        assert list(df.columns) == ["商品编号", "商品名称", "采购数量", "采购单价", "采购日期"]

    def test_load_nonexistent_file_raises_error(self):
        engine = ExcelEngine()
        with pytest.raises(FileNotFoundError):
            engine.load_file("/nonexistent/path.xlsx")


class TestExcelEngineMultiMatch:
    def test_single_match_left_join(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        rules = [
            {"target_sheet": "销售记录", "match_column": "商品编号",
             "bring_columns": ["销售数量", "销售单价"], "how": "left"}
        ]
        result = engine.multi_match("采购明细", rules)
        assert "销售数量" in result.columns
        assert "销售单价" in result.columns
        assert len(result) == 4
        assert result.loc[result["商品编号"] == "A004", "销售数量"].isna().values[0]

    def test_multi_match_chained(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        rules = [
            {"target_sheet": "销售记录", "match_column": "商品编号",
             "bring_columns": ["销售数量", "销售单价"], "how": "left"},
            {"target_sheet": "库存表", "match_column": "商品编号",
             "bring_columns": ["当前库存", "仓库位置"], "how": "left"},
        ]
        result = engine.multi_match("采购明细", rules)
        assert "销售数量" in result.columns
        assert "当前库存" in result.columns
        assert len(result) == 4

    def test_match_inner_join(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        rules = [{"target_sheet": "销售记录", "match_column": "商品编号",
                  "bring_columns": ["销售数量"], "how": "inner"}]
        result = engine.multi_match("采购明细", rules)
        assert len(result) == 3

    def test_match_column_not_found_raises(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        rules = [{"target_sheet": "销售记录", "match_column": "采购日期",
                  "bring_columns": ["销售数量"], "how": "inner"}]
        with pytest.raises(ValueError, match="未找到列"):
            engine.multi_match("采购明细", rules)


class TestExcelEngineFilter:
    def test_filter_equals(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.filter_data("采购明细", column="商品编号", op="equals", value="A001")
        assert len(result) == 1
        assert result.iloc[0]["商品名称"] == "笔记本电脑"

    def test_filter_contains(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.filter_data("采购明细", column="商品名称", op="contains", value="电脑")
        assert len(result) == 1  # 只有"笔记本电脑"包含"电脑"

    def test_filter_greater_than(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.filter_data("采购明细", column="采购单价", op="greater_than", value=500)
        assert len(result) == 2


class TestExcelEngineDedup:
    def test_dedup_keep_first(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.dedup_data("采购明细", columns=["商品编号"], keep="first")
        assert len(result) == 4


class TestExcelEngineSort:
    def test_sort_ascending(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.sort_data("采购明细", columns=["采购单价"], ascending=[True])
        assert result.iloc[0]["采购单价"] == 50

    def test_sort_descending(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.sort_data("采购明细", columns=["采购单价"], ascending=[False])
        assert result.iloc[0]["采购单价"] == 3500


class TestExcelEngineGroup:
    def test_group_sum(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        rules = [{"target_sheet": "商品信息", "match_column": "商品编号",
                  "bring_columns": ["分类"], "how": "left"}]
        matched = engine.multi_match("采购明细", rules)
        engine._sheets["采购带分类"] = matched
        result = engine.group_data("采购带分类", group_columns=["分类"],
                                    agg_column="采购数量", agg_func="sum")
        assert len(result) == 2
        elec_sum = result[result["分类"] == "电子产品"]["采购数量"].values[0]
        assert elec_sum == 50 + 100 + 30

    def test_group_count(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        engine._sheets["采购带分类"] = engine.multi_match("采购明细", [
            {"target_sheet": "商品信息", "match_column": "商品编号",
             "bring_columns": ["分类"], "how": "left"}
        ])
        result = engine.group_data("采购带分类", group_columns=["分类"],
                                    agg_column="商品编号", agg_func="count")
        assert result[result["分类"] == "电子产品"]["商品编号"].values[0] == 3

    def test_group_mean(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        engine._sheets["采购带分类"] = engine.multi_match("采购明细", [
            {"target_sheet": "商品信息", "match_column": "商品编号",
             "bring_columns": ["分类"], "how": "left"}
        ])
        result = engine.group_data("采购带分类", group_columns=["分类"],
                                    agg_column="采购单价", agg_func="mean")
        elec_mean = result[result["分类"] == "电子产品"]["采购单价"].values[0]
        assert elec_mean == (3500 + 250 + 1800) / 3


class TestExcelEngineMergeSheets:
    def test_vertical_concat(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        # 不去重的上下拼接：8行
        result = engine.merge_sheets(
            sheet_names=["采购明细", "库存表"],
            mode="vertical",
            match_column=None
        )
        assert len(result) == 8

    def test_vertical_concat_with_dedup(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        # 按商品编号去重：4行（两个表商品编号相同）
        result = engine.merge_sheets(
            sheet_names=["采购明细", "库存表"],
            mode="vertical",
            match_column="商品编号"
        )
        assert len(result) == 4

    def test_horizontal_merge(self, sample_excel_path):
        engine = ExcelEngine()
        engine.load_file(sample_excel_path)
        result = engine.merge_sheets(
            sheet_names=["采购明细", "库存表"],
            mode="horizontal",
            match_column="商品编号"
        )
        assert "当前库存" in result.columns
        assert "采购数量" in result.columns
        assert len(result) == 4