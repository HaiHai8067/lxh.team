"""
自定义 fixtures 示例
文件名以 fixture_ 开头，会被框架自动加载

使用方法：
1. 在本目录新建 fixture_xxx.py 文件
2. 定义带 @pytest.fixture 装饰器的函数
3. 在测试用例中直接作为参数使用
"""

import pytest


@pytest.fixture
def sample_data():
    """
    示例 fixture - 可根据需要修改或删除

    Returns:
        示例测试数据
    """
    return {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@lxh.dev",
    }
