"""
响应数据提取器
支持多种方式从响应中提取数据
"""

import re
from typing import Any, List, Optional


class Extractor:
    """
    响应数据提取器

    支持多种提取方式：
    - JSONPath: $.data.id
    - XPath: 暂未实现（HTML/XML）
    - 正则: regex:.*token=(\w+)
    - Header: header:Authorization
    - Cookie: cookie:session_id
    """
    @staticmethod
    def from_json(data: Any, expression: str) -> Any:
        """
        从 JSON 数据中提取

        Args:
            data: JSON 数据（dict/list）
            expression: 提取表达式

        Returns:
            提取的值
        """
        if expression.startswith("$"):
            # JSONPath 格式
            return Extractor._extract_jsonpath(data, expression)
        else:
            # 点分隔路径
            return Extractor._extract_dot_path(data, expression)

    @staticmethod
    def _extract_jsonpath(data: Any, expression: str) -> Any:
        """JSONPath 提取"""
        try:
            from jsonpath_ng import parse
            jsonpath_expr = parse(expression)
            matches = [match.value for match in jsonpath_expr.find(data)]
            if len(matches) == 1:
                return matches[0]
            return matches if matches else None
        except Exception:
            return None

    @staticmethod
    def _extract_dot_path(data: Any, path: str) -> Any:
        """点分隔路径提取"""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                return None
        return current

    @staticmethod
    def from_text(text: str, pattern: str) -> Optional[str]:
        """
        从文本中用正则提取

        Args:
            text: 文本内容
            pattern: 正则表达式

        Returns:
            提取的第一个匹配组，或 None
        """
        match = re.search(pattern, text)
        if match:
            if match.groups():
                return match.group(1)
            return match.group(0)
        return None

    @staticmethod
    def from_header(headers: dict, name: str) -> Optional[str]:
        """
        从响应头中提取

        Args:
            headers: 响应头字典
            name: Header 名称（不区分大小写）

        Returns:
            Header 值，或 None
        """
        name_lower = name.lower()
        for k, v in headers.items():
            if k.lower() == name_lower:
                return v
        return None

    @staticmethod
    def from_cookie(cookies: dict, name: str) -> Optional[str]:
        """
        从 Cookie 中提取

        Args:
            cookies: Cookie 字典
            name: Cookie 名称

        Returns:
            Cookie 值，或 None
        """
        return cookies.get(name)
