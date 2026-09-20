"""
pytest 全局配置文件 - LXH 框架入口

LXH 框架通过 pytest 插件自动加载，无需手动导入。
你可以在这里添加项目级别的自定义 fixture。
"""

import sys
from pathlib import Path

# 自动加载 fixtures 目录中的 fixture_*.py 模块
_fixtures_dir = Path(__file__).parent / "fixtures"
if _fixtures_dir.exists() and _fixtures_dir.is_dir():
    _fixtures_dir_str = str(_fixtures_dir)
    if _fixtures_dir_str not in sys.path:
        sys.path.insert(0, _fixtures_dir_str)

    # 注册为 pytest 插件
    pytest_plugins = []
    for _f in _fixtures_dir.glob("fixture_*.py"):
        pytest_plugins.append(_f.stem)
