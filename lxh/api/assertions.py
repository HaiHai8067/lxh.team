"""
API 断言库
提供流式的 API 断言方法
"""

from lxh.api.http import HttpResponse
from typing import Any, List, Optional


class ApiAssert:
    """
    API 断言工具类

    提供流式 API 断言接口，支持链式调用。

    Examples:
        >>> ApiAssert(response) \\
        ...     .status_ok() \\
        ...     .json_has("code") \\
        ...     .json_equal("message", "success") \\
        ...     .time_less_than(1.0)
    """
