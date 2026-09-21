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


# ============================================================
# HttpResponse 测试
# ============================================================


class TestHttpResponse:
    """HttpResponse 响应封装测试类"""

    def test_status_code(self):
        """测试 status_code 属性"""
        mock_resp = make_mock_response(status_code=200)
        resp = HttpResponse(mock_resp)
        assert resp.status_code == 200

    def test_status_code_404(self):
        """测试 404 状态码"""
        mock_resp = make_mock_response(
            status_code=404, json_data={"error": "not found"}
        )
        resp = HttpResponse(mock_resp)
        assert resp.status_code == 404
        assert resp.ok is False

    def test_url_property(self):
        """测试 url 属性"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        assert resp.url == "https://api.example.com/test"

    def test_headers_property(self):
        """测试 headers 属性"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        assert resp.headers["Content-Type"] == "application/json"
        assert resp.headers["X-Request-Id"] == "req-12345"

    def test_text_property(self):
        """测试 text 属性"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        assert "test_user" in resp.text

