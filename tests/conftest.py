import pytest
import pandas as pd
import tempfile
import os


@pytest.fixture
def sample_excel_path():
    """创建包含4个sheet的样本Excel文件，返回文件路径"""
    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    path = tmp.name
    tmp.close()

    purchase_data = {
        "商品编号": ["A001", "A002", "A003", "A004"],
        "商品名称": ["笔记本电脑", "机械键盘", "显示器", "鼠标"],
        "采购数量": [50, 100, 30, 200],
        "采购单价": [3500, 250, 1800, 50],
        "采购日期": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
    }

    sales_data = {
        "商品编号": ["A001", "A002", "A003"],
        "销售数量": [30, 80, 20],
        "销售单价": [4200, 350, 2200],
        "销售日期": ["2024-02-01", "2024-02-02", "2024-02-03"],
    }

    inventory_data = {
        "商品编号": ["A001", "A002", "A003", "A004"],
        "当前库存": [20, 20, 10, 180],
        "仓库位置": ["A区", "B区", "A区", "C区"],
    }

    product_data = {
        "商品编号": ["A001", "A002", "A003", "A004"],
        "分类": ["电子产品", "电子产品", "电子产品", "配件"],
        "品牌": ["Lenovo", "Logitech", "Dell", "Logitech"],
    }

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(purchase_data).to_excel(writer, sheet_name="采购明细", index=False)
        pd.DataFrame(sales_data).to_excel(writer, sheet_name="销售记录", index=False)
        pd.DataFrame(inventory_data).to_excel(writer, sheet_name="库存表", index=False)
        pd.DataFrame(product_data).to_excel(writer, sheet_name="商品信息", index=False)

    yield path
    try:
        os.unlink(path)
    except PermissionError:
        pass