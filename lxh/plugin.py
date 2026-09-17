"""
LXH pytest 插件
实现 fixture 自动加载、环境管理、报告增强等核心功能
"""

import sys
import pytest
from pathlib import Path

from lxh.core.config import EnvConfig
from lxh import __version__, __slogan__, __author__

# 导入内置 fixtures 到当前命名空间，pytest 会自动发现
from lxh.fixtures.fixture_builtin import (
    lxh_env,
    lxh_config,
    lxh_project_root,
    lxh_tests_dir,
    lxh_data_dir,
    lxh_reports_dir,
    lxh_vars,
    lxh_module_vars,
    lxh_logger,
)

# API 测试 fixtures
try:
    from lxh.fixtures.fixture_api import lxh_api_client, lxh_api
except ImportError:
    pass


def pytest_configure(config):
    """pytest 配置钩子"""
    # 注册自定义标记
    markers = [
        ("smoke", "冒烟测试用例"),
        ("regression", "回归测试用例"),
        ("api", "API 测试用例"),
        ("ui", "UI 测试用例"),
        ("perf", "性能测试用例"),
        ("p0", "P0 级别用例"),
        ("p1", "P1 级别用例"),
        ("p2", "P2 级别用例"),
    ]
    for name, desc in markers:
        config.addinivalue_line("markers", f"{name}: {desc}")

    # 初始化日志
    from lxh.core.logger import setup_logger
    rootdir = str(config.rootdir)
    setup_logger(log_dir=str(Path(rootdir) / "reports" / "logs"))


def pytest_sessionstart(session):
    """pytest 会话开始钩子"""
    if session.config.option.verbose > 0:
        print()
        print("=" * 60)
        print(f"  ⚡ LXH v{__version__} - {__slogan__}")
        print("=" * 60)
        print()


def pytest_addoption(parser):
    """添加命令行选项"""
    group = parser.getgroup("lxh", "LXH 框架选项")

    group.addoption(
        "--env",
        action="store",
        default="test",
        help="指定运行环境: dev/test/staging/prod，默认 test"
    )

    group.addoption(
        "--env-config",
        action="store",
        default=None,
        help="指定环境配置文件路径，默认 env.yaml"
    )
