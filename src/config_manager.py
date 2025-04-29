
import json
from pathlib import Path

class ConfigManager:
    DEFAULT_CONFIG = {
        "hotkey": "<ctrl>+<alt>+q",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key": "",
        "model": "Qwen/Qwen2-VL-72B-Instruct",
        "prompt": "请分析这张截图内容并给出简洁回复",
        "knowledge": ""
    }

    def __init__(self):
        self.config_path = Path.home() / '.snipechat_config.json'
        self.config = self.load_config()

    def load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()

    def save_config(self, config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        self.config = config

    def get(self, key, default=None):
        return self.config.get(key, default)
