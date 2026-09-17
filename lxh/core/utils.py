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
            "random_str": self._func_random_str,
        }

    # 如下部分是内置函数
    @staticmethod
    def _func_random_str(length: str = "8") -> str:
        """生成随机字符串"""
        n = int(length)
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))


if __name__ == "__main__":
    v_e = VarEngine()
    print(v_e._func_random_str())
