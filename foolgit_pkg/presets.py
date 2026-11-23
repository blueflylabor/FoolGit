"""
FoolGit 预设功能库与元数据定义
支持根据当前语言动态渲染名称与描述。
"""

from typing import Dict, Any, List
from .i18n import t

# 出厂默认启用的核心功能 ID 列表 (仅 6 个日常最高频项)
DEFAULT_ACTIVE_IDS = ["sync", "pull", "status", "undo", "branch", "stash"]

# 所有官方预设功能的 ID 顺序列表
ALL_PRESET_IDS = [
    "sync", "pull", "status", "undo", "branch", "stash",
    "history", "diff", "clean", "tag", "remote", "multi_sync"
]


def get_preset_info(preset_id: str) -> Dict[str, Any]:
    """获取指定预设功能的本地化元数据"""
    is_builtin = preset_id in DEFAULT_ACTIVE_IDS
    return {
        "id": preset_id,
        "name": t(f"preset_{preset_id}_name"),
        "tag": t(f"preset_{preset_id}_tag"),
        "short_desc": t(f"preset_{preset_id}_desc"),
        "is_builtin": is_builtin,
        "default_enabled": is_builtin,
    }


def get_preset_library() -> Dict[str, Dict[str, Any]]:
    """获取所有预设功能库字典 (动态本地化)"""
    return {pid: get_preset_info(pid) for pid in ALL_PRESET_IDS}
