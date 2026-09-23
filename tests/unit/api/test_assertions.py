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
