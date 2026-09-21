"""
HTTP 客户端模块单元测试
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from lxh.api.http import HttpClient, HttpResponse

# ---- 测试数据 ----

SAMPLE_JSON = {
    "code": 0,
    "message": "success",
    "data": {
        "id": 1001,
        "name": "test_user",
        "email": "test@lxh.dev",
        "roles": ["admin", "user"],
        "profile": {
            "age": 25,
            "city": "Beijing",
        },
    },
}

SAMPLE_HEADERS = {
    "Content-Type": "application/json",
    "X-Request-Id": "req-12345",
    "Server": "nginx",
}


def make_mock_response(
    status_code=200,
    json_data=None,
    text=None,
    headers=None,
    elapsed=0.123,
):
    """创建模拟 Response 对象"""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.status_code = status_code
    mock_resp.headers = headers or SAMPLE_HEADERS.copy()
    mock_resp.url = "https://api.example.com/test"
    mock_resp.text = text or json.dumps(json_data or {})
    mock_resp.content = mock_resp.text.encode("utf-8")
    mock_resp.ok = 200 <= status_code < 300

    # 模拟 elapsed（timedelta）
    from datetime import timedelta

    mock_resp.elapsed = timedelta(seconds=elapsed)

    # 模拟 json() 方法
    if json_data is not None:
        mock_resp.json.return_value = json_data
    else:
        mock_resp.json.side_effect = ValueError("No JSON")

    return mock_resp
