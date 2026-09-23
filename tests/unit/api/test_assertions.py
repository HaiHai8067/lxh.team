"""
断言库模块单元测试
"""

from unittest.mock import MagicMock

import pytest
import requests

from lxh.api.assertions import ApiAssert
from lxh.api.http import HttpResponse


def make_response(json_data=None, status_code=200, headers=None, elapsed=0.1):
    """创建模拟 HttpResponse"""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.status_code = status_code
    mock_resp.headers = headers or {"Content-Type": "application/json"}
    mock_resp.url = "https://api.example.com/test"
    mock_resp.text = '{"test": true}'
    mock_resp.content = mock_resp.text.encode()
    mock_resp.ok = 200 <= status_code < 300

    from datetime import timedelta

    mock_resp.elapsed = timedelta(seconds=elapsed)

    if json_data is not None:
        mock_resp.json.return_value = json_data
        mock_resp.text = __import__("json").dumps(json_data)
    else:
        mock_resp.json.side_effect = ValueError("No JSON")

    return HttpResponse(mock_resp)


SAMPLE_DATA = {
    "code": 0,
    "message": "success",
    "data": {
        "id": 1001,
        "name": "test_user",
        "email": "test@lxh.dev",
        "tags": ["a", "b", "c"],
        "profile": {"age": 25, "city": "Beijing"},
    },
    "list": [{"id": 1}, {"id": 2}, {"id": 3}],
}


class TestApiAssertStatus:
    """状态码断言测试"""

    def test_status_ok_200(self):
        """测试 200 状态码通过"""
        resp = make_response(json_data={}, status_code=200)
        ApiAssert(resp).status_ok()

    def test_status_ok_201(self):
        """测试 201 状态码通过"""
        resp = make_response(json_data={}, status_code=201)
        ApiAssert(resp).status_ok()

    def test_status_ok_204(self):
        """测试 204 状态码通过"""
        resp = make_response(json_data=None, status_code=204)
        ApiAssert(resp).status_ok()

    def test_status_ok_400_fail(self):
        """测试 400 状态码断言失败"""
        resp = make_response(json_data={}, status_code=400)
        with pytest.raises(AssertionError):
            ApiAssert(resp).status_ok()

    def test_status_exact_pass(self):
        """测试精确状态码断言通过"""
        resp = make_response(json_data={}, status_code=201)
        ApiAssert(resp).status(201)

    def test_status_exact_fail(self):
        """测试精确状态码断言失败"""
        resp = make_response(json_data={}, status_code=200)
        with pytest.raises(AssertionError):
            ApiAssert(resp).status(201)

    def test_status_in_pass(self):
        """测试 status_in 断言通过"""
        resp = make_response(json_data={}, status_code=201)
        ApiAssert(resp).status_in([200, 201, 204])

    def test_status_in_fail(self):
        """测试 status_in 断言失败"""
        resp = make_response(json_data={}, status_code=400)
        with pytest.raises(AssertionError):
            ApiAssert(resp).status_in([200, 201])


class TestApiAssertJson:
    """JSON 断言测试"""

    def test_json_has_simple(self):
        """测试简单字段存在断言"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_has("code")

    def test_json_has_nested(self):
        """测试嵌套字段存在断言"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_has("data.name")
        ApiAssert(resp).json_has("data.profile.age")

    def test_json_has_fail(self):
        """测试字段不存在时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_has("nonexistent")

    def test_json_has_nested_fail(self):
        """测试嵌套字段不存在时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_has("data.nonexistent")

    def test_json_equal_pass(self):
        """测试字段值相等断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_equal("code", 0)
        ApiAssert(resp).json_equal("data.name", "test_user")
        ApiAssert(resp).json_equal("data.profile.age", 25)

    def test_json_equal_fail(self):
        """测试字段值不相等时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_equal("code", 1)

    def test_json_not_equal_pass(self):
        """测试字段值不等断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_not_equal("code", 1)

    def test_json_not_equal_fail(self):
        """测试字段值相等时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_not_equal("code", 0)

    def test_json_contains_pass(self):
        """测试字符串包含断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_contains("message", "success")
        ApiAssert(resp).json_contains("data.email", "@lxh.dev")

    def test_json_contains_fail(self):
        """测试字符串不包含时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_contains("message", "error")

    def test_json_type_pass(self):
        """测试类型断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_type("code", int)
        ApiAssert(resp).json_type("data.name", str)
        ApiAssert(resp).json_type("data.tags", list)
        ApiAssert(resp).json_type("data.profile", dict)

    def test_json_type_fail(self):
        """测试类型不匹配时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_type("code", str)

    def test_json_length_pass(self):
        """测试长度断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_length("data.tags", 3)
        ApiAssert(resp).json_length("data.name", 9)

    def test_json_length_fail(self):
        """测试长度不匹配时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_length("data.tags", 5)

    def test_json_list_has_item_pass(self):
        """测试列表包含元素断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_list_has_item("data.tags", "a")

    def test_json_list_has_item_fail(self):
        """测试列表不包含元素时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).json_list_has_item("data.tags", "d")


class TestApiAssertTime:
    """响应时间断言测试"""

    def test_time_less_than_pass(self):
        """测试响应时间断言通过"""
        resp = make_response(json_data={}, elapsed=0.1)
        ApiAssert(resp).time_less_than(1.0)

    def test_time_less_than_fail(self):
        """测试响应时间断言失败"""
        resp = make_response(json_data={}, elapsed=2.0)
        with pytest.raises(AssertionError, match="响应时间断言失败"):
            ApiAssert(resp).time_less_than(1.0)

    def test_time_greater_than_pass(self):
        """测试响应时间大于断言通过"""
        resp = make_response(json_data={}, elapsed=0.5)
        ApiAssert(resp).time_greater_than(0.1)

    def test_time_greater_than_fail(self):
        """测试响应时间大于断言失败"""
        resp = make_response(json_data={}, elapsed=0.1)
        with pytest.raises(AssertionError):
            ApiAssert(resp).time_greater_than(0.5)


class TestApiAssertBody:
    """响应体断言测试"""

    def test_body_contains_pass(self):
        """测试响应体包含断言通过"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).body_contains("test_user")

    def test_body_contains_fail(self):
        """测试响应体不包含时断言失败"""
        resp = make_response(json_data=SAMPLE_DATA)
        with pytest.raises(AssertionError):
            ApiAssert(resp).body_contains("nonexistent_text_xyz")


class TestApiAssertChaining:
    """链式调用测试"""

    def test_full_chain(self):
        """测试完整的链式断言"""
        resp = make_response(json_data=SAMPLE_DATA, status_code=200, elapsed=0.1)
        (
            ApiAssert(resp)
            .status_ok()
            .json_has("code")
            .json_equal("code", 0)
            .json_has("data.id")
            .time_less_than(1.0)
            .header_has("Content-Type")
        )

    def test_chain_returns_self(self):
        """测试每个断言方法都返回 self"""
        resp = make_response(json_data=SAMPLE_DATA)
        assertion = ApiAssert(resp)

        assert assertion.status_ok() is assertion
        assert assertion.json_has("code") is assertion
        assert assertion.json_equal("code", 0) is assertion
        assert assertion.time_less_than(1.0) is assertion

    def test_response_property(self):
        """测试 response 属性"""
        resp = make_response(json_data=SAMPLE_DATA)
        assertion = ApiAssert(resp)
        assert assertion.response is resp


class TestApiAssertJsonpath:
    """JSONPath 语法断言测试"""

    def test_json_has_jsonpath(self):
        """测试 JSONPath 语法的字段存在断言"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_has("$.data.id")

    def test_json_equal_jsonpath(self):
        """测试 JSONPath 语法的值相等断言"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_equal("$.data.name", "test_user")

    def test_json_type_jsonpath(self):
        """测试 JSONPath 语法的类型断言"""
        resp = make_response(json_data=SAMPLE_DATA)
        ApiAssert(resp).json_type("$.data.tags", list)
