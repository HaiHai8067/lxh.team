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

    def time_less_than(self, seconds: float) -> "ApiAssert":
        """断言响应时间小于指定值（秒）"""
        self._response.assert_time_less_than(seconds)
        return self

    def time_greater_than(self, seconds: float) -> "ApiAssert":
        """断言响应时间大于指定值（秒）"""
        assert self._response.elapsed > seconds, (
            f"响应时间断言失败: 期望 > {seconds}s, 实际 {self._response.elapsed:.3f}s"
        )
        return self

    # ---- Header断言 ----

    def header_has(self, header: str) -> "ApiAssert":
        """断言响应头包含指定字段"""
        self._response.assert_header_contains(header)
        return self

    def header_equal(self, header: str, value: str) -> "ApiAssert":
        """断言响应头字段等于指定值"""
        headers_lower = {k.lower(): v for k, v in self._response.headers.items()}
        header_lower = header.lower()
        assert header_lower in headers_lower, f"响应头中找不到: {header}"
        assert headers_lower[header_lower] == value, (
            f"响应头断言失败: {header} 期望 {value}, 实际 {headers_lower[header_lower]}"
        )
        return self

    # ---- 内容断言 ----

    def body_contains(self, text: str) -> "ApiAssert":
        """断言响应体包含指定文本"""
        assert text in self._response.text, (
            f"响应体断言失败: 不包含 '{text}'"
        )
        return self

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

    @property
    def response(self) -> HttpResponse:
        """获取原始响应对象"""
        return self._response
