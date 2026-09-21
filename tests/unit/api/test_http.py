"""
HTTP 客户端模块单元测试
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from lxh.api.http import HttpClient, HttpResponse
