"""
LXH pytest 插件
实现 fixture 自动加载、环境管理、报告增强等核心功能
"""

import sys
import pytest
from pathlib import Path

from lxh import __version__, __slogan__, __author__


# 导入内置 fixtures 到当前命名空间，让 pytest 自动发现
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
