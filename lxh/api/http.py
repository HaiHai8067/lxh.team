"""
HTTP 请求客户端封装
基于 requests 库的统一 HTTP 客户端，支持会话管理、钩子机制、自动日志等
"""

import json
import time
import requests
from urllib.parse import urljoin
from requests import Response, Session
from typing import Any, Dict, Optional, Union


from lxh.core.utils import VarEngine
from lxh.core.logger import get_logger


logger = get_logger("lxh:http")


class HttpResponse:
    """
    HTTP 响应封装
    对 requests.Response 进行扩展，提供便捷的断言和提取方法
    """

    def __init__(self, response: Response, request_info: dict = None):
        self._response = response
        self._request_info = request_info or {}
        self._json_cache = None

    @property
    def status_code(self) -> int:
        """响应状态码"""
        return self._response.status_code

    @property
    def url(self) -> str:
        """请求 URL"""
        return self._response.url

    @property
    def headers(self) -> dict:
        """响应头"""
        return dict(self._response.headers)

    @property
    def text(self) -> str:
        """响应文本"""
        return self._response.text

    @property
    def content(self) -> bytes:
        """响应字节内容"""
        return self._response.content

    @property
    def elapsed(self) -> float:
        """响应时间（秒）"""
        return self._response.elapsed.total_seconds()

    @property
    def ok(self) -> bool:
        """请求是否成功（状态码 < 400）"""
        return self._response.ok

    @property
    def raw(self) -> Response:
        """原始 Response 对象"""
        return self._response

    def json(self, **kwargs) -> Any:
        """
        解析 JSON 响应

        Returns:
            解析后的 JSON 数据
        """
        if self._json_cache is None:
            try:
                self._json_cache = self._response.json(**kwargs)
            except (json.JSONDecodeError, ValueError):
                self._json_cache = None
        return self._json_cache

    def extract(self, expression: str) -> Any:
        """
        从响应中提取数据

        支持 JSONPath 表达式，如:
        - $.data.id
        - $.data.list[0].name
        - $.data.users[*].name

        Args:
            expression: JSONPath 表达式

        Returns:
            提取的值
        """
        from jsonpath_ng import parse

        data = self.json()
        if data is None:
            return None

        try:
            jsonpath_expr = parse(expression)
            matches = [match.value for match in jsonpath_expr.find(data)]
            if len(matches) == 1:
                return matches[0]
            return matches if matches else None
        except Exception:
            return None


class HttpClient:
    """
    HTTP 客户端

    基于 requests.Session 封装，提供统一的 HTTP 请求方法，
    支持会话保持、钩子机制、自动日志、变量替换等功能。

    Examples:
        >>> client = HttpClient(base_url="https://api.example.com")
        >>> resp = client.get("/users/1")
        >>> resp.assert_status_ok()
        >>> resp.assert_json_contains("id", 1)
    """