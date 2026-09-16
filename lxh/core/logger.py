"""
日志管理模块
基于 loguru 封装的统一日志系统
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional

# 日志是否已初始化
_initialized = False


def get_logger(name: str = "lxh"):
    """
    获取 logger 实例

    Args:
        name: logger 名称
    """
    if not _initialized:
        _setup_default_logger()

    return logger.bind(name=name)


def _setup_default_logger():
    """配置默认日志"""
    global _initialized

    # 移除默认 handler
    logger.remove()

    # 控制台输出格式

