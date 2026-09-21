"""
pytest 全局配置 - LXH 框架测试
"""

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

pytest_plugins = []
