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

    def set(self, key: str, value: Any):
        """设置变量"""
        keys = key.split(".")
        current = self._context

        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取变量"""
        return self._get_nested_value(self._context, key, default)

    def update(self, data: Dict[str, Any]):
        """批量更新变量"""
        self._context.update(data)

    def clear(self):
        """清空所有变量"""
        self._context.clear()

    def render(self, template: Any) -> Any:
        """
        渲染模板，替换变量

        Args:
            template: 模板内容（字符串、字典、列表）

        Returns:
            替换后的结果
        """
        if isinstance(template, str):
            return self._render_string(template)
        elif isinstance(template, dict):
            return {k: self.render(v) for k, v in template.items()}
        elif isinstance(template, list):
            return [self.render(item) for item in template]
        else:
            return template

    def _render_string(self, template: str) -> Any:
        """渲染字符串模板"""
        if not template:
            return template

            # 如果整个字符串就是一个变量，直接返回原值（保持类型）
        match = _VAR_PATTERN.fullmatch(template.strip())
        if match:
            var_expr = match.group(1).strip()
            return self._resolve_expression(var_expr)

        # 替换所有变量
        def replace_var(m):
            var_expr = m.group(1).strip()
            result = self._resolve_expression(var_expr)
            return str(result) if result is not None else m.group(0)

        return _VAR_PATTERN.sub(replace_var, template)

    def _resolve_expression(self, expr: str) -> Any:
        """解析变量表达式"""
        # 函数调用语法: func_name(arg1, arg2)
        func_match = re.match(r"^(\w+)\((.*)\)$", expr)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2).strip()
            if args_str:
                args = [arg.strip() for arg in args_str.split(",")]
            else:
                args = []
            return self._call_function(func_name, args)

        # 普通变量路径
        return self.get(expr)

    def _call_function(self, func_name: str, args: list) -> Any:
        """调用内置函数"""
        if func_name in self._functions:
            try:
                return self._functions[func_name](*args)
            except Exception:
                return None
        return None

    @staticmethod
    def _get_nested_value(data: dict, path: str, default: Any = None) -> Any:
        """获取嵌套字典值"""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

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


# 全局默认实例
_default_engine = VarEngine()


def v(template: Any, context: Optional[Dict[str, Any]] = None) -> Any:
    """
    变量替换函数 v()

    支持 ${变量名} 语法，支持嵌套变量，支持函数调用。

    Args:
        template: 模板内容
        context: 变量上下文字典

    Returns:
        替换后的结果

    Examples:
        >>> v("Hello ${name}", {"name": "World"})
        'Hello World'
        >>> v("${random_str(6)}")
        'aBcDeF'
        >>> v("${user.name}", {"user": {"name": "Tom"}})
        'Tom'
    """
    engine = _default_engine
    if context is not None:
        engine = VarEngine()
        engine.update(context)
    return engine.render(template)
