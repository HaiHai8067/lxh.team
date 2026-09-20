"""
示例测试用例
演示 LXH 框架的基本使用方式
"""

import pytest


def test_lxh_basic():
    """基础示例测试"""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"


def test_lxh_env_fixture(lxh_env, lxh_project_root):
    """测试环境 fixture"""
    assert lxh_env in ["dev", "test", "staging", "prod"]
    assert lxh_project_root.exists()


def test_lxh_vars_fixture(lxh_vars):
    """测试变量存储 fixture"""
    lxh_vars["token"] = "abc123"
    lxh_vars["user_id"] = 1001

    assert lxh_vars["token"] == "abc123"
    assert lxh_vars["user_id"] == 1001


def test_lxh_config_fixture(lxh_config):
    """测试环境配置 fixture"""
    assert lxh_config.env in ["dev", "test", "staging", "prod"]
    # 配置可以通过 .get() 获取
    # base_url = lxh_config.get("base_url", "http://localhost")


def test_lxh_logger_fixture(lxh_logger):
    """测试日志 fixture"""
    lxh_logger.info("这是一条测试日志")
    lxh_logger.success("测试用例执行成功")


@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (10, 20, 30),
    (100, 200, 300),
])
def test_lxh_parametrize(a, b, expected):
    """参数化测试示例"""
    assert a + b == expected
