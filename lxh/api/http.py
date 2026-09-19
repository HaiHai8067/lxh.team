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

    # 相关断言方法
    def assert_status(self, expected: int) -> "HttpResponse":
        """
        断言状态码

        Args:
            expected: 期望的状态码

        Returns:
            self（链式调用）

        Raises:
            AssertionError: 状态码不匹配
        """
        assert self.status_code == expected, (
            f"状态码断言失败: 期望 {expected}, 实际 {self.status_code}"
        )
        logger.success(f"✅ 状态码断言通过: {self.status_code}")
        return self

    def assert_status_ok(self) -> "HttpResponse":
        """断言请求成功（2xx）"""
        assert 200 <= self.status_code < 300, (
            f"状态码断言失败: 期望 2xx, 实际 {self.status_code}"
        )
        logger.success(f"✅ 状态码断言通过: {self.status_code}")
        return self

    def assert_json_contains(self, key: str, value: Any = None) -> "HttpResponse":
        """
        断言 JSON 响应包含指定字段

        Args:
            key: 字段路径（支持点分隔，如 "data.id"）
            value: 期望值（可选）

        Returns:
            self
        """
        data = self.json()
        assert data is not None, "响应不是有效的 JSON"

        keys = key.split(".")
        current = data
        for k in keys:
            assert isinstance(current, dict) and k in current, (
                f"JSON 中找不到字段: {key}"
            )
            current = current[k]

        if value is not None:
            assert current == value, (
                f"字段 {key} 值断言失败: 期望 {value}, 实际 {current}"
            )
            logger.success(f"✅ 字段断言通过: {key} = {value}")
        else:
            logger.success(f"✅ 字段存在: {key}")

        return self

    def assert_time_less_than(self, seconds: float) -> "HttpResponse":
        """
        断言响应时间小于指定值

        Args:
            seconds: 期望的最大响应时间（秒）

        Returns:
            self
        """
        assert self.elapsed < seconds, (
            f"响应时间断言失败: 期望 < {seconds}s, 实际 {self.elapsed:.3f}s"
        )
        logger.success(f"✅ 响应时间断言通过: {self.elapsed:.3f}s")
        return self

    def assert_header_contains(self, header: str, value: str = None) -> "HttpResponse":
        """
        断言响应头包含指定字段

        Args:
            header: 响应头名称
            value: 期望值（可选）

        Returns:
            self
        """
        header_lower = header.lower()
        headers_lower = {k.lower(): v for k, v in self.headers.items()}

        assert header_lower in headers_lower, f"响应头中找不到: {header}"

        if value is not None:
            actual = headers_lower[header_lower]
            assert value in actual, (
                f"响应头 {header} 值断言失败: 期望包含 {value}, 实际 {actual}"
            )
            logger.success(f"✅ 响应头断言通过: {header} 包含 {value}")
        else:
            logger.success(f"✅ 响应头存在: {header}")

        return self

    def __repr__(self) -> str:
        return f"HttpResponse(status={self.status_code}, elapsed={self.elapsed:.3f}s)"


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

    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify: bool = True,
        session: Optional[Session] = None,
    ):
        """
        初始化 HTTP 客户端

        Args:
            base_url: 基础 URL，所有请求会拼接此地址
            headers: 默认请求头
            timeout: 默认超时时间（秒）
            verify: 是否验证 SSL 证书
            session: 自定义 requests Session
        """
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.timeout = timeout
        self.verify = verify
        self.session = session or Session()
        self._var_engine = VarEngine()

        if headers:
            self.session.headers.update(headers)

        # 钩子函数列表
        self._request_hooks = []
        self._response_hooks = []

    # ---- 公共方法 ----

    def set_base_url(self, base_url: str):
        """设置基础 URL"""
        self.base_url = base_url.rstrip("/") if base_url else ""

    def set_header(self, key: str, value: str):
        """设置请求头"""
        self.session.headers[key] = value

    def set_headers(self, headers: Dict[str, str]):
        """批量设置请求头"""
        self.session.headers.update(headers)

    def set_var(self, key: str, value: Any):
        """设置变量"""
        self._var_engine.set(key, value)

    def get_var(self, key: str, default: Any = None) -> Any:
        """获取变量"""
        return self._var_engine.get(key, default)

    def add_request_hook(self, hook_func):
        """
        添加请求前钩子

        Hook 函数签名: hook_func(method, url, kwargs) -> (url, kwargs)
        """
        self._request_hooks.append(hook_func)

    def add_response_hook(self, hook_func):
        """
        添加响应后钩子

        Hook 函数签名: hook_func(response) -> response
        """
        self._response_hooks.append(hook_func)

    # ---- HTTP 方法 ----

    def get(self, url: str, **kwargs) -> HttpResponse:
        """发送 GET 请求"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> HttpResponse:
        """发送 POST 请求"""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> HttpResponse:
        """发送 PUT 请求"""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> HttpResponse:
        """发送 DELETE 请求"""
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> HttpResponse:
        """发送 PATCH 请求"""
        return self.request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs) -> HttpResponse:
        """发送 HEAD 请求"""
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs) -> HttpResponse:
        """发送 OPTIONS 请求"""
        return self.request("OPTIONS", url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            url: 请求 URL（相对路径会自动拼接 base_url）
            **kwargs: 传递给 requests 的参数

        Returns:
            HttpResponse 对象
        """
        # 构造完整 URL
        full_url = self._build_url(url)

        # 变量替换
        full_url = self._var_engine.render(full_url)
        if "params" in kwargs:
            kwargs["params"] = self._var_engine.render(kwargs["params"])
        if "json" in kwargs:
            kwargs["json"] = self._var_engine.render(kwargs["json"])
        if "data" in kwargs:
            kwargs["data"] = self._var_engine.render(kwargs["data"])
        if "headers" in kwargs:
            kwargs["headers"] = self._var_engine.render(kwargs["headers"])

        # 设置默认超时和 verify
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify)

        # 记录请求信息
        request_info = {
            "method": method,
            "url": full_url,
            "start_time": time.time(),
        }

        # 执行请求前钩子
        for hook in self._request_hooks:
            try:
                result = hook(method, full_url, kwargs)
                if result and isinstance(result, tuple) and len(result) == 2:
                    full_url, kwargs = result
            except Exception as e:
                logger.warning(f"请求钩子执行失败: {e}")

        # 发送请求
        logger.info(f"📤 {method} {full_url}")

        try:
            response = self.session.request(method, full_url, **kwargs)
        except requests.RequestException as e:
            logger.error(f"❌ 请求失败: {e}")
            raise

        # 记录响应信息
        elapsed = time.time() - request_info["start_time"]
        request_info["elapsed"] = elapsed

        # 封装响应
        http_response = HttpResponse(response, request_info)

        logger.info(
            f"📥 {response.status_code} {method} {full_url} "
            f"({elapsed:.3f}s)"
        )

        # 执行响应后钩子
        for hook in self._response_hooks:
            try:
                http_response = hook(http_response) or http_response
            except Exception as e:
                logger.warning(f"响应钩子执行失败: {e}")

        return http_response

    # ---- 内部方法 ----

    def _build_url(self, url: str) -> str:
        """构造完整 URL"""
        if url.startswith(("http://", "https://")):
            return url
        if self.base_url:
            return f"{self.base_url}/{url.lstrip('/')}"
        return url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def __repr__(self) -> str:
        return f"HttpClient(base_url='{self.base_url}')"
