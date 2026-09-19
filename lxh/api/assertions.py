"""
API 断言库
提供流式的 API 断言方法
"""

from lxh.api.http import HttpResponse
from typing import Any, List, Optional


class ApiAssert:
    """
    API 断言工具类

    提供流式 API 断言接口，支持链式调用。

    Examples:
        >>> ApiAssert(response) \\
        ...     .status_ok() \\
        ...     .json_has("code") \\
        ...     .json_equal("message", "success") \\
        ...     .time_less_than(1.0)
    """

    def __init__(self, response: HttpResponse):
        self._response = response
        self._data = response.json() if response.json() is not None else {}

    # ---- 状态码断言 ----

    def status_ok(self) -> "ApiAssert":
        """断言状态码为 2xx"""
        self._response.assert_status_ok()
        return self

    def status(self, code: int) -> "ApiAssert":
        """断言状态码等于指定值"""
        self._response.assert_status(code)
        return self

    def status_in(self, codes: List[int]) -> "ApiAssert":
        """断言状态码在列表中"""
        assert self._response.status_code in codes, (
            f"状态码断言失败: 期望 {codes}, 实际 {self._response.status_code}"
        )
        return self

    # ---- JSON 断言 ----

    def json_has(self, path: str) -> "ApiAssert":
        """断言 JSON 包含指定路径的字段"""
        value = self._get_json_value(path)
        assert value is not None, f"JSON 断言失败: 字段 '{path}' 不存在"
        return self

    def json_equal(self, path: str, expected: Any) -> "ApiAssert":
        """断言 JSON 字段值等于期望值"""
        actual = self._get_json_value(path)
        assert actual == expected, (
            f"JSON 断言失败: '{path}' 期望 {expected}, 实际 {actual}"
        )
        return self

    def json_not_equal(self, path: str, expected: Any) -> "ApiAssert":
        """断言 JSON 字段值不等于期望值"""
        actual = self._get_json_value(path)
        assert actual != expected, (
            f"JSON 断言失败: '{path}' 期望不等于 {expected}"
        )
        return self

    def json_contains(self, path: str, substring: str) -> "ApiAssert":
        """断言 JSON 字符串字段包含子串"""
        actual = self._get_json_value(path)
        assert isinstance(actual, str) and substring in actual, (
            f"JSON 断言失败: '{path}' 期望包含 '{substring}', 实际 '{actual}'"
        )
        return self

    def json_type(self, path: str, expected_type: type) -> "ApiAssert":
        """断言 JSON 字段类型"""
        actual = self._get_json_value(path)
        assert isinstance(actual, expected_type), (
            f"JSON 断言失败: '{path}' 期望类型 {expected_type.__name__}, "
            f"实际类型 {type(actual).__name__}"
        )
        return self

    def json_length(self, path: str, length: int) -> "ApiAssert":
        """断言 JSON 数组/字符串长度"""
        actual = self._get_json_value(path)
        assert len(actual) == length, (
            f"JSON 断言失败: '{path}' 期望长度 {length}, 实际 {len(actual)}"
        )
        return self

    def json_list_has_item(self, path: str, item: Any) -> "ApiAssert":
        """断言 JSON 数组包含指定元素"""
        actual = self._get_json_value(path)
        assert isinstance(actual, list) and item in actual, (
            f"JSON 断言失败: 列表 '{path}' 不包含 {item}"
        )
        return self

    # ---- 响应时间断言 ----



    # ---- 辅助方法 ----

    def _get_json_value(self, path: str) -> Any:
        """获取 JSON 字段值"""
        if not path or "$" == path:
            return self._data

        # 支持 JSONPath 格式
        if path.startswith("$"):
            return self._response.extract(path)

        # 支持点分隔路径
        keys = path.split(".")
        current = self._data
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
