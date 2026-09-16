"""
API 测试 fixtures
提供 API 测试相关的内置 fixture
"""

import pytest


@pytest.fixture(scope="session")
def lxh_api_client(lxh_config):
    """
    会话级 API 客户端 fixture

    从环境配置中读取 base_url 和默认 headers，
    创建一个共享的 HttpClient 实例。

    Returns:
        HttpClient: API 客户端实例
    """

@pytest.fixture(scope="function")
def lxh_api(lxh_config):
    """
    用例级 API 客户端 fixture

    每个用例使用独立的客户端，避免会话污染。

    Returns:
        HttpClient: API 客户端实例
    """