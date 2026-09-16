"""
LXH 内置 fixtures
提供框架基础的 fixture 集合
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def lxh_env(request):
    """
    获取当前运行环境名称

    Returns:
        str: 环境名称 (dev/test/staging/prod)
    """
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def lxh_config(request):
    """
    获取环境配置

    Returns:
        EnvConfig: 环境配置对象
    """
    pass


@pytest.fixture(scope="session")
def lxh_project_root(request):
    """
    获取项目根目录路径

    Returns:
        Path: 项目根目录 Path 对象
    """
    return Path(request.config.rootdir)


@pytest.fixture(scope="session")
def lxh_tests_dir(request):
    """
    获取 tests 目录路径

    Returns:
        Path: tests 目录 Path 对象
    """

    return Path(request.config.rootdir) / "tests"


@pytest.fixture(scope="session")
def lxh_data_dir(request):
    """
    获取 data 目录路径

    Returns:
        Path: data 目录 Path 对象
    """
    return Path(request.config.rootdir) / "data"


@pytest.fixture(scope="session")
def lxh_reports_dir(request):
    """
    获取 reports 目录路径

    Returns:
        Path: reports 目录 Path 对象
    """
    return Path(request.config.rootdir) / "reports"


@pytest.fixture(scope="function")
def lxh_vars():
    """
    用例级变量存储 fixture

    用于在测试步骤之间传递变量，支持 ${变量名} 方式引用。

    Returns:
        dict: 可变字典，用于存储用例变量

    Example:
        def test_example(lxh_vars):
            lxh_vars["token"] = "abc123"
            assert lxh_vars["token"] == "abc123"
    """
    variables = {}
    yield variables
    variables.clear()


@pytest.fixture(scope="module")
def lxh_module_vars():
    """
    模块级变量存储 fixture

    用于同一测试模块内多个用例之间共享变量。

    Returns:
        dict: 可变字典，用于存储模块变量
    """
    variables = {}
    yield variables
    variables.clear()


@pytest.fixture(scope="function")
def lxh_logger(request):
    """
    用例级 logger fixture

    每个用例有独立的 logger，自动记录用例名称。

    Returns:
        logger: loguru logger 实例
    """
    pass


