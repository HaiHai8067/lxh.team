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
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        filter=lambda record: record["level"].no < 40,
        # WARNING 以下走 stdout
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level="WARNING",
    )

    _initialized = True


def setup_logger(
    log_dir: Optional[str] = None,
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "30 days",
):
    """
        配置日志（带文件输出）

        Args:
            log_dir: 日志文件目录
            level: 日志级别
            rotation: 日志轮转条件
            retention: 日志保留时长
        """
    global _initialized

    logger.remove()

    # 控制台输出
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=console_format,
        level=level,
        filter=lambda record: record["level"].no < 40,
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level="WARNING",
    )

    # 文件输出
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{extra[name]} | "
            "{message}"
        )

        logger.add(
            log_path / "lxh_{time:YYYY-MM-DD}.log",
            format=file_format,
            level=level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
        )

    _initialized = True
