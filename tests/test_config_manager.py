import pytest
import tempfile
import os
from src.config_manager import ConfigManager


@pytest.fixture
def config_dir():
    tmp = tempfile.mkdtemp()
    yield tmp
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def manager(config_dir):
    return ConfigManager(config_dir)


class TestConfigManager:
    def test_save_and_load_config(self, manager):
        config = {
            "operation": "multi_match",
            "base_sheet": "采购明细",
            "rules": [
                {"target_sheet": "销售记录", "match_column": "商品编号",
                 "bring_columns": ["销售数量"], "how": "left"}
            ],
        }
        name = "月度进销存汇总"
        manager.save_config(name, config)
        loaded = manager.load_config(name)
        assert loaded == config

    def test_list_configs(self, manager):
        manager.save_config("配置A", {"operation": "filter"})
        manager.save_config("配置B", {"operation": "group"})
        names = manager.list_configs()
        assert "配置A" in names
        assert "配置B" in names

    def test_load_nonexistent_config_raises(self, manager):
        with pytest.raises(FileNotFoundError):
            manager.load_config("不存在的配置")

    def test_delete_config(self, manager):
        manager.save_config("临时配置", {"operation": "sort"})
        manager.delete_config("临时配置")
        assert "临时配置" not in manager.list_configs()