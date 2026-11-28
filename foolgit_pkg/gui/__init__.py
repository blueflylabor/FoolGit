"""
FoolGit 极简图形化交互界面 (GUI) 包入口
导出与原单文件模块完全兼容的接口。
"""

from .theme import DARK_QSS
from .window import FoolGitMainWindow, GitTaskThread, launch_gui

__all__ = ["DARK_QSS", "GitTaskThread", "FoolGitMainWindow", "launch_gui"]
