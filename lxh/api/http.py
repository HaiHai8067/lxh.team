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