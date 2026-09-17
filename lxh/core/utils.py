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
            "random_int": self._func_random_int,
            "timestamp": self._func_timestamp,
            "datetime": self._func_datetime,
            "uuid": self._func_uuid,
        }

    # 如下部分是内置函数
    @staticmethod
    def _func_random_str(length: str = "8") -> str:
        """生成随机字符串"""
        n = int(length)
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @staticmethod
    def _func_random_int(min_val: str = "1", max_val: str = "100") -> int:
        """生成随机整数"""
        return random.randint(int(min_val), int(max_val))

    @staticmethod
    def _func_timestamp() -> int:
        """获取当前时间戳"""
        return int(datetime.now().timestamp())

    @staticmethod
    def _func_datetime(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前格式化时间"""
        return datetime.now().strftime(fmt)

    @staticmethod
    def _func_uuid() -> str:
        """生成 UUID"""
        import uuid
        return str(uuid.uuid4())

    @property
    def context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return self._context.copy()


if __name__ == "__main__":
    v_e = VarEngine()
    print(v_e._func_random_str())
