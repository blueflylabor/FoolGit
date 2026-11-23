"""
FoolGit 用户配置管理器
负责 ~/.foolgit/config.json 的读写、出厂设置恢复、语言设置与自定义命令增删改查。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .presets import DEFAULT_ACTIVE_IDS, ALL_PRESET_IDS
from .i18n import set_language, get_language, DEFAULT_LANG


def get_default_config_path() -> Path:
    """获取配置文件路径，带自动降级与权限保护"""
    env_dir = os.environ.get("FOOLGIT_CONFIG_DIR")
    if env_dir:
        return Path(env_dir) / "config.json"

    primary_dir = Path.home() / ".foolgit"
    try:
        primary_dir.mkdir(parents=True, exist_ok=True)
        # 测试是否可写
        test_file = primary_dir / ".perm_check"
        test_file.touch()
        test_file.unlink()
        return primary_dir / "config.json"
    except (PermissionError, OSError):
        # 无法写入用户家目录时降级到当前目录或临时目录
        local_dir = Path(".foolgit")
        try:
            local_dir.mkdir(parents=True, exist_ok=True)
            return local_dir / "config.json"
        except (PermissionError, OSError):
            import tempfile
            return Path(tempfile.gettempdir()) / ".foolgit_config.json"


def get_default_config() -> Dict[str, Any]:
    """生成出厂默认配置结构，默认语言为英文 (en)"""
    return {
        "version": "1.0.0",
        "language": DEFAULT_LANG,  # "en" 默认英文
        "active_preset_ids": list(DEFAULT_ACTIVE_IDS),
        "custom_commands": [],
        "settings": {
            "default_commit_prefix": "update: ",
            "auto_pull_before_push": True,
            "confirm_before_push": False,
        }
    }


class ConfigManager:
    """管理 FoolGit 的配置持久化与变更"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or get_default_config_path()
        self._memory_cache = get_default_config()
        self._ensure_config()
        # 初始化 i18n 语言
        cfg = self.load()
        set_language(cfg.get("language", DEFAULT_LANG))

    def _ensure_config(self) -> None:
        """确保配置目录与文件存在，不存在则自动初始化"""
        try:
            if not self.config_path.exists():
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                self.save(get_default_config())
            else:
                self.load()
        except Exception:
            pass

    def load(self) -> Dict[str, Any]:
        """读取配置文件，并做平滑兼容升级"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 补齐可能缺失的字段
            defaults = get_default_config()
            for key, val in defaults.items():
                if key not in data:
                    data[key] = val
            self._memory_cache = data
            return data
        except Exception:
            return self._memory_cache

    def save(self, data: Dict[str, Any]) -> None:
        """保存配置到磁盘"""
        self._memory_cache = data
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_language(self) -> str:
        """获取当前配置语言"""
        cfg = self.load()
        return cfg.get("language", DEFAULT_LANG)

    def set_language(self, lang: str) -> None:
        """设置并持久化语言配置"""
        set_language(lang)
        cfg = self.load()
        cfg["language"] = lang
        self.save(cfg)

    def get_active_preset_ids(self) -> List[str]:
        """获取当前启用的预设命令 ID 列表"""
        cfg = self.load()
        return cfg.get("active_preset_ids", list(DEFAULT_ACTIVE_IDS))

    def enable_preset(self, preset_id: str) -> bool:
        """从备选库中启用某个功能"""
        if preset_id not in ALL_PRESET_IDS:
            return False
        cfg = self.load()
        active = cfg.get("active_preset_ids", [])
        if preset_id not in active:
            active.append(preset_id)
            cfg["active_preset_ids"] = active
            self.save(cfg)
        return True

    def disable_preset(self, preset_id: str) -> bool:
        """从主菜单停用某个功能"""
        cfg = self.load()
        active = cfg.get("active_preset_ids", [])
        if preset_id in active:
            active.remove(preset_id)
            cfg["active_preset_ids"] = active
            self.save(cfg)
            return True
        return False

    def get_custom_commands(self) -> List[Dict[str, str]]:
        """获取所有用户自定义命令"""
        cfg = self.load()
        return cfg.get("custom_commands", [])

    def add_custom_command(self, name: str, cmd: str, desc: str = "") -> str:
        """添加一条自定义命令"""
        cfg = self.load()
        commands = cfg.get("custom_commands", [])
        import time
        cmd_id = f"custom_{int(time.time())}"
        new_cmd = {
            "id": cmd_id,
            "name": name.strip(),
            "cmd": cmd.strip(),
            "desc": desc.strip() or cmd.strip(),
        }
        commands.append(new_cmd)
        cfg["custom_commands"] = commands
        self.save(cfg)
        return cmd_id

    def remove_custom_command(self, cmd_id: str) -> bool:
        """删除一条自定义命令"""
        cfg = self.load()
        commands = cfg.get("custom_commands", [])
        new_cmds = [c for c in commands if c.get("id") != cmd_id]
        if len(new_cmds) != len(commands):
            cfg["custom_commands"] = new_cmds
            self.save(cfg)
            return True
        return False

    def reset_to_defaults(self) -> None:
        """重置回出厂默认状态"""
        self.save(get_default_config())
        set_language(DEFAULT_LANG)
