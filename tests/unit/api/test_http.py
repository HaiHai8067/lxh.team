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

    def test_elapsed_property(self):
        """测试 elapsed 属性"""
        mock_resp = make_mock_response(elapsed=0.5)
        resp = HttpResponse(mock_resp)
        assert resp.elapsed == 0.5

    def test_ok_property_200(self):
        """测试 ok 属性（200 状态码）"""
        mock_resp = make_mock_response(status_code=200)
        resp = HttpResponse(mock_resp)
        assert resp.ok is True

    def test_ok_property_500(self):
        """测试 ok 属性（500 状态码）"""
        mock_resp = make_mock_response(status_code=500, json_data={})
        resp = HttpResponse(mock_resp)
        assert resp.ok is False

    def test_json_method(self):
        """测试 json() 方法"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "test_user"

    def test_json_cache(self):
        """测试 JSON 缓存"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        # 调用两次
        resp.json()
        resp.json()
        # json() 方法应该被调用了一次（被缓存了）
        # 注意：这里 mock_resp.json 还是被调用了一次，
        # 但 HttpResponse 内部应该缓存了结果
        assert mock_resp.json.call_count == 1

    def test_json_invalid(self):
        """测试无效 JSON 响应"""
        mock_resp = make_mock_response(text="not json")
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        resp = HttpResponse(mock_resp)
        assert resp.json() is None

    def test_extract_simple_path(self):
        """测试简单路径提取"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        result = resp.extract("$.data.id")
        assert result == 1001

    def test_extract_nested_path(self):
        """测试嵌套路径提取"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        result = resp.extract("$.data.profile.city")
        assert result == "Beijing"

    def test_extract_list_item(self):
        """测试列表元素提取"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        result = resp.extract("$.data.roles[0]")
        assert result == "admin"

    def test_extract_nonexistent(self):
        """测试不存在的路径"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        result = resp.extract("$.data.nonexistent")
        assert result is None

    def test_extract_invalid_json(self):
        """测试无效 JSON 时提取返回 None"""
        mock_resp = make_mock_response(text="not json")
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        resp = HttpResponse(mock_resp)
        assert resp.extract("$.data.id") is None

    # ---- 断言方法测试 ----

    def test_assert_status_pass(self):
        """测试状态码断言通过"""
        mock_resp = make_mock_response(status_code=200)
        resp = HttpResponse(mock_resp)
        result = resp.assert_status(200)
        assert result is resp  # 链式调用

    def test_assert_status_fail(self):
        """测试状态码断言失败"""
        mock_resp = make_mock_response(status_code=404, json_data={})
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError, match="状态码断言失败"):
            resp.assert_status(200)

    def test_assert_status_ok_pass(self):
        """测试 status_ok 断言通过"""
        mock_resp = make_mock_response(status_code=201)
        resp = HttpResponse(mock_resp)
        result = resp.assert_status_ok()
        assert result is resp

    def test_assert_status_ok_fail(self):
        """测试 status_ok 断言失败"""
        mock_resp = make_mock_response(status_code=400, json_data={})
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError):
            resp.assert_status_ok()

    def test_assert_json_contains_key(self):
        """测试 JSON 包含字段断言"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        result = resp.assert_json_contains("code")
        assert result is resp

    def test_assert_json_contains_nested_key(self):
        """测试 JSON 包含嵌套字段"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        resp.assert_json_contains("data.name")

    def test_assert_json_contains_with_value(self):
        """测试 JSON 字段值断言"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        resp.assert_json_contains("code", 0)
        resp.assert_json_contains("data.name", "test_user")

    def test_assert_json_contains_key_missing(self):
        """测试 JSON 字段不存在时断言失败"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError):
            resp.assert_json_contains("nonexistent")

    def test_assert_json_contains_value_mismatch(self):
        """测试 JSON 字段值不匹配时断言失败"""
        mock_resp = make_mock_response(json_data=SAMPLE_JSON)
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError):
            resp.assert_json_contains("code", 1)

    def test_assert_json_contains_invalid_json(self):
        """测试无效 JSON 时断言失败"""
        mock_resp = make_mock_response(text="not json")
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError, match="不是有效的 JSON"):
            resp.assert_json_contains("code")

    def test_assert_time_less_than_pass(self):
        """测试响应时间断言通过"""
        mock_resp = make_mock_response(elapsed=0.1)
        resp = HttpResponse(mock_resp)
        result = resp.assert_time_less_than(1.0)
        assert result is resp

    def test_assert_time_less_than_fail(self):
        """测试响应时间断言失败"""
        mock_resp = make_mock_response(elapsed=2.0)
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError, match="响应时间断言失败"):
            resp.assert_time_less_than(1.0)

    def test_assert_header_contains_pass(self):
        """测试响应头断言通过"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        result = resp.assert_header_contains("Content-Type")
        assert result is resp

    def test_assert_header_contains_with_value(self):
        """测试响应头值断言"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        resp.assert_header_contains("Content-Type", "application/json")

    def test_assert_header_contains_missing(self):
        """测试响应头不存在时断言失败"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        with pytest.raises(AssertionError):
            resp.assert_header_contains("X-Nonexistent")

    def test_raw_property(self):
        """测试 raw 属性返回原始 Response"""
        mock_resp = make_mock_response()
        resp = HttpResponse(mock_resp)
        assert resp.raw is mock_resp

    def test_repr(self):
        """测试 __repr__ 方法"""
        mock_resp = make_mock_response(status_code=200, elapsed=0.123)
        resp = HttpResponse(mock_resp)
        repr_str = repr(resp)
        assert "200" in repr_str
        assert "0.123" in repr_str


