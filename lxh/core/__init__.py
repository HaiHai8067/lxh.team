"""
LXH 核心模块
包含框架基础功能：配置、日志、工具函数、插件机制等
"""

from lxh.core.config import EnvConfig, get_env_config
# from lxh.core.utils import v, VarEngine
# from lxh.core.logger import get_logger

__all__ = [
    "EnvConfig",
    "get_env_config",
    "v",
    "VarEngine",
    "get_logger",
]
