"""
工具函数模块
包含变量替换、常用工具函数等
"""

import re
import os
import random
import string
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

# ${变量名} 正则表达式
_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


class VarEngine:
    """变量替换引擎"""
    def __init__(self):
        self._context: Dict[str, Any] = {}
        self._functions: Dict[str, callable] = {

        }