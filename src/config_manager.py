import json
import os


class ConfigManager:
    """操作配置的 JSON 保存/加载"""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".excel_tools_configs")
        self._dir = config_dir
        os.makedirs(self._dir, exist_ok=True)

    def save_config(self, name: str, config: dict) -> None:
        """保存操作配置为 JSON 文件"""
        safe_name = name.replace("/", "_").replace("\\", "_")
        path = os.path.join(self._dir, f"{safe_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_config(self, name: str) -> dict:
        """加载操作配置"""
        safe_name = name.replace("/", "_").replace("\\", "_")
        path = os.path.join(self._dir, f"{safe_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"未找到配置: {name}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_configs(self) -> list[str]:
        """列出所有已保存的配置名称"""
        configs = []
        for fname in os.listdir(self._dir):
            if fname.endswith(".json"):
                configs.append(fname[:-5])
        return configs

    def delete_config(self, name: str) -> None:
        """删除配置"""
        safe_name = name.replace("/", "_").replace("\\", "_")
        path = os.path.join(self._dir, f"{safe_name}.json")
        if os.path.exists(path):
            os.remove(path)