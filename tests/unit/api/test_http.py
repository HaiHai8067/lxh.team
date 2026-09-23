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


# ============================================================
# HttpClient 测试
# ============================================================


class TestHttpClient:
    """HttpClient 测试类"""

    def test_init_with_base_url(self):
        """测试带 base_url 初始化"""
        client = HttpClient(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"

    def test_init_strips_trailing_slash(self):
        """测试 base_url 去掉末尾斜杠"""
        client = HttpClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"

    def test_init_with_headers(self):
        """测试带默认 headers 初始化"""
        client = HttpClient(headers={"Authorization": "Bearer token"})
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer token"

    def test_set_base_url(self):
        """测试设置 base_url"""
        client = HttpClient()
        client.set_base_url("https://api.new.com")
        assert client.base_url == "https://api.new.com"

    def test_set_header(self):
        """测试设置单个 header"""
        client = HttpClient()
        client.set_header("X-Custom", "value")
        assert client.session.headers["X-Custom"] == "value"

    def test_set_headers(self):
        """测试批量设置 headers"""
        client = HttpClient()
        client.set_headers({"X-1": "a", "X-2": "b"})
        assert client.session.headers["X-1"] == "a"
        assert client.session.headers["X-2"] == "b"

    def test_set_and_get_var(self):
        """测试设置和获取变量"""
        client = HttpClient()
        client.set_var("token", "abc123")
        assert client.get_var("token") == "abc123"
        assert client.get_var("nonexistent", "default") == "default"

    @patch.object(requests.Session, "request")
    def test_get_request(self, mock_request):
        """测试 GET 请求"""
        mock_request.return_value = make_mock_response(
            status_code=200, json_data={"result": "ok"}
        )

        client = HttpClient(base_url="https://api.example.com")
        resp = client.get("/users")

        assert resp.status_code == 200
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "GET"
        assert "users" in call_args[0][1]

    @patch.object(requests.Session, "request")
    def test_post_request_with_json(self, mock_request):
        """测试带 JSON body 的 POST 请求"""
        mock_request.return_value = make_mock_response(
            status_code=201, json_data={"id": 1}
        )

        client = HttpClient(base_url="https://api.example.com")
        resp = client.post("/users", json={"name": "test"})

        assert resp.status_code == 201
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert call_args[1]["json"] == {"name": "test"}

    @patch.object(requests.Session, "request")
    def test_put_request(self, mock_request):
        """测试 PUT 请求"""
        mock_request.return_value = make_mock_response(
            status_code=200, json_data={"updated": True}
        )

        client = HttpClient(base_url="https://api.example.com")
        resp = client.put("/users/1", json={"name": "updated"})

        assert resp.status_code == 200
        call_args = mock_request.call_args
        assert call_args[0][0] == "PUT"

    @patch.object(requests.Session, "request")
    def test_delete_request(self, mock_request):
        """测试 DELETE 请求"""
        mock_request.return_value = make_mock_response(status_code=204, json_data=None)
        mock_request.return_value.json.side_effect = ValueError("No JSON")

        client = HttpClient(base_url="https://api.example.com")
        resp = client.delete("/users/1")

        assert resp.status_code == 204
        call_args = mock_request.call_args
        assert call_args[0][0] == "DELETE"

    @patch.object(requests.Session, "request")
    def test_patch_request(self, mock_request):
        """测试 PATCH 请求"""
        mock_request.return_value = make_mock_response(
            status_code=200, json_data={"patched": True}
        )

        client = HttpClient(base_url="https://api.example.com")
        resp = client.patch("/users/1", json={"name": "patched"})

        assert resp.status_code == 200
        call_args = mock_request.call_args
        assert call_args[0][0] == "PATCH"

    def test_full_url_construction(self):
        """测试完整 URL 构造"""
        client = HttpClient(base_url="https://api.example.com/api/v1")

        # 相对路径
        assert client._build_url("users") == "https://api.example.com/api/v1/users"
        assert client._build_url("/users") == "https://api.example.com/api/v1/users"

        # 绝对路径
        assert client._build_url("https://other.com/api") == "https://other.com/api"

    @patch.object(requests.Session, "request")
    def test_variable_replacement_in_url(self, mock_request):
        """测试 URL 中的变量替换"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com")
        client.set_var("user_id", 1001)
        client.get("/users/${user_id}")

        call_args = mock_request.call_args
        assert "users/1001" in call_args[0][1]

    @patch.object(requests.Session, "request")
    def test_variable_replacement_in_params(self, mock_request):
        """测试 params 中的变量替换（完整匹配保留原始类型）"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com")
        client.set_var("page", 2)
        client.get("/users", params={"page": "${page}", "size": 10})

        call_args = mock_request.call_args
        # 完整匹配变量时保留原始类型（int）
        assert call_args[1]["params"]["page"] == 2
        assert call_args[1]["params"]["size"] == 10

    @patch.object(requests.Session, "request")
    def test_variable_replacement_in_json(self, mock_request):
        """测试 JSON body 中的变量替换"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com")
        client.set_var("username", "test_user")
        client.post("/users", json={"name": "${username}", "age": 18})

        call_args = mock_request.call_args
        assert call_args[1]["json"]["name"] == "test_user"
        assert call_args[1]["json"]["age"] == 18

    @patch.object(requests.Session, "request")
    def test_request_hook(self, mock_request):
        """测试请求钩子"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com")
        hook_called = []

        def my_hook(method, url, kwargs):
            hook_called.append((method, url))
            kwargs["headers"] = {"X-Hook": "true"}
            return url, kwargs

        client.add_request_hook(my_hook)
        client.get("/test")

        assert len(hook_called) == 1
        assert hook_called[0][0] == "GET"
        call_args = mock_request.call_args
        assert call_args[1]["headers"]["X-Hook"] == "true"

    @patch.object(requests.Session, "request")
    def test_response_hook(self, mock_request):
        """测试响应钩子"""
        mock_request.return_value = make_mock_response(
            status_code=200, json_data={"code": 0}
        )

        client = HttpClient(base_url="https://api.example.com")
        hook_called = []

        def my_hook(response):
            hook_called.append(response.status_code)
            return response

        client.add_response_hook(my_hook)
        resp = client.get("/test")

        assert len(hook_called) == 1
        assert hook_called[0] == 200
        assert resp.status_code == 200

    @patch.object(requests.Session, "request")
    def test_request_failure_raises(self, mock_request):
        """测试请求失败时抛出异常"""
        mock_request.side_effect = requests.ConnectionError("Connection failed")

        client = HttpClient(base_url="https://api.example.com")
        with pytest.raises(requests.ConnectionError):
            client.get("/test")

    def test_context_manager(self):
        """测试上下文管理器"""
        with HttpClient(base_url="https://api.example.com") as client:
            assert client.base_url == "https://api.example.com"
        # 退出后 session 应该被关闭
        # （Session 没有 close 状态，这里只验证不抛异常）

    def test_repr(self):
        """测试 __repr__ 方法"""
        client = HttpClient(base_url="https://api.example.com")
        repr_str = repr(client)
        assert "HttpClient" in repr_str
        assert "api.example.com" in repr_str

    @patch.object(requests.Session, "request")
    def test_default_timeout(self, mock_request):
        """测试默认超时设置"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com", timeout=10)
        client.get("/test")

        call_args = mock_request.call_args
        assert call_args[1]["timeout"] == 10

    @patch.object(requests.Session, "request")
    def test_verify_ssl(self, mock_request):
        """测试 SSL 验证设置"""
        mock_request.return_value = make_mock_response(status_code=200, json_data={})

        client = HttpClient(base_url="https://api.example.com", verify=False)
        client.get("/test")

        call_args = mock_request.call_args
        assert call_args[1]["verify"] is False
