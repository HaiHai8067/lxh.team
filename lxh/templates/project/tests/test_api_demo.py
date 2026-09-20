"""
API 测试示例
演示 LXH 框架的 API 测试用法

使用前请确保配置好 base_url（在 env.yaml 中），
或直接在代码中指定 base_url。
"""

import pytest


def test_api_get_example(lxh_api):
    """
    示例：GET 请求测试
    使用 lxh_api fixture 创建的 HTTP 客户端
    """
    # TODO: 替换为实际的接口地址
    # resp = lxh_api.get("/api/users")
    # resp.assert_status_ok()
    # resp.assert_json_contains("code", 0)

    # 以下为占位断言
    assert True


def test_api_post_example(lxh_api, lxh_vars):
    """
    示例：POST 请求 + 变量传递
    """
    # 1. 登录获取 token
    # resp = lxh_api.post("/api/login", json={
    #     "username": "test",
    #     "password": "123456"
    # })
    # token = resp.extract("$.data.token")
    # lxh_vars["token"] = token

    # 2. 使用 token 请求其他接口
    # lxh_api.set_header("Authorization", f"Bearer ${token}")
    # resp2 = lxh_api.get("/api/user/info")
    # resp2.assert_status_ok()

    assert lxh_vars is not None


def test_api_assert_example(lxh_api):
    """
    示例：ApiAssert 链式断言
    """
    # from lxh.api import ApiAssert
    # resp = lxh_api.get("/api/users/1")
    # ApiAssert(resp) \\
    #     .status_ok() \\
    #     .json_has("data.id") \\
    #     .json_equal("data.username", "testuser") \\
    #     .time_less_than(1.0)

    assert True


def test_api_var_replace_example(lxh_api):
    """
    示例：变量替换
    """
    # lxh_api.set_var("user_id", 1001)
    # resp = lxh_api.get("/api/user/${user_id}")
    # resp.assert_status_ok()

    assert True


@pytest.mark.api
@pytest.mark.p0
def test_api_p0_marker():
    """
    示例：使用标记装饰器
    运行方式:
    - pytest -m api      # 只跑 API 测试
    - pytest -m p0       # 只跑 P0 级别
    - pytest -m "api and p0"  # API + P0
    """
    assert True
