"""
提取器模块单元测试
"""

from lxh.api.extractor import Extractor

SAMPLE_DATA = {
    "code": 0,
    "message": "success",
    "data": {
        "id": 1001,
        "name": "test_user",
        "email": "test@lxh.dev",
        "roles": ["admin", "editor", "viewer"],
        "profile": {
            "age": 25,
            "city": "Beijing",
        },
    },
    "items": [
        {"id": 1, "name": "item1"},
        {"id": 2, "name": "item2"},
        {"id": 3, "name": "item3"},
    ],
}


class TestExtractorFromJson:
    """JSON 提取测试"""

    def test_dot_path_simple(self):
        """测试点分隔简单路径"""
        result = Extractor.from_json(SAMPLE_DATA, "code")
        assert result == 0

    def test_dot_path_nested(self):
        """测试点分隔嵌套路径"""
        result = Extractor.from_json(SAMPLE_DATA, "data.name")
        assert result == "test_user"

    def test_dot_path_deeply_nested(self):
        """测试深层嵌套路径"""
        result = Extractor.from_json(SAMPLE_DATA, "data.profile.city")
        assert result == "Beijing"

    def test_dot_path_list_index(self):
        """测试点路径中的列表索引"""
        result = Extractor.from_json(SAMPLE_DATA, "data.roles.0")
        assert result == "admin"

    def test_dot_path_nonexistent(self):
        """测试不存在的路径返回 None"""
        result = Extractor.from_json(SAMPLE_DATA, "nonexistent")
        assert result is None

    def test_dot_path_nested_nonexistent(self):
        """测试嵌套路径不存在时返回 None"""
        result = Extractor.from_json(SAMPLE_DATA, "data.nonexistent.field")
        assert result is None

    def test_dot_path_list_out_of_range(self):
        """测试列表索引越界返回 None"""
        result = Extractor.from_json(SAMPLE_DATA, "data.roles.100")
        assert result is None

    def test_jsonpath_simple(self):
        """测试 JSONPath 简单路径"""
        result = Extractor.from_json(SAMPLE_DATA, "$.code")
        assert result == 0

    def test_jsonpath_nested(self):
        """测试 JSONPath 嵌套路径"""
        result = Extractor.from_json(SAMPLE_DATA, "$.data.name")
        assert result == "test_user"

    def test_jsonpath_list_item(self):
        """测试 JSONPath 列表元素"""
        result = Extractor.from_json(SAMPLE_DATA, "$.data.roles[0]")
        assert result == "admin"

    def test_jsonpath_list_all(self):
        """测试 JSONPath 列表所有元素"""
        result = Extractor.from_json(SAMPLE_DATA, "$.items[*].name")
        assert isinstance(result, list)
        assert len(result) == 3
        assert "item1" in result

    def test_jsonpath_nonexistent(self):
        """测试 JSONPath 不存在的路径"""
        result = Extractor.from_json(SAMPLE_DATA, "$.nonexistent")
        assert result is None

    def test_jsonpath_deeply_nested(self):
        """测试 JSONPath 深层嵌套"""
        result = Extractor.from_json(SAMPLE_DATA, "$.data.profile.age")
        assert result == 25

    def test_from_empty_dict(self):
        """测试从空字典提取"""
        result = Extractor.from_json({}, "code")
        assert result is None

    def test_from_list_root(self):
        """测试根为列表的情况"""
        data = [1, 2, 3]
        result = Extractor.from_json(data, "$[0]")
        assert result == 1

    def test_root_path_dollar(self):
        """测试根路径 $ 返回整个数据"""
        result = Extractor.from_json(SAMPLE_DATA, "$")
        assert result == SAMPLE_DATA


class TestExtractorFromText:
    """文本提取测试"""

    def test_simple_pattern(self):
        """测试简单正则提取"""
        text = "token=abc123xyz"
        result = Extractor.from_text(text, r"token=(\w+)")
        assert result == "abc123xyz"

    def test_no_group_returns_full_match(self):
        """测试没有捕获组时返回完整匹配"""
        text = "hello world"
        result = Extractor.from_text(text, r"hello")
        assert result == "hello"

    def test_no_match_returns_none(self):
        """测试没有匹配时返回 None"""
        text = "hello world"
        result = Extractor.from_text(text, r"token=(\w+)")
        assert result is None

    def test_multiple_matches_returns_first(self):
        """测试多个匹配时返回第一个"""
        text = "id=1, id=2, id=3"
        result = Extractor.from_text(text, r"id=(\d+)")
        assert result == "1"

    def test_html_pattern(self):
        """测试 HTML 内容提取"""
        html = '<div class="user">John</div>'
        result = Extractor.from_text(html, r'class="user">(\w+)<')
        assert result == "John"


class TestExtractorFromHeader:
    """Header 提取测试"""

    def test_extract_existing_header(self):
        """测试提取存在的 header"""
        headers = {"Content-Type": "application/json", "X-Token": "abc123"}
        result = Extractor.from_header(headers, "X-Token")
        assert result == "abc123"

    def test_extract_case_insensitive(self):
        """测试 header 名称不区分大小写"""
        headers = {"Content-Type": "application/json"}
        result = Extractor.from_header(headers, "content-type")
        assert result == "application/json"

    def test_extract_missing_header(self):
        """测试提取不存在的 header 返回 None"""
        headers = {"Content-Type": "application/json"}
        result = Extractor.from_header(headers, "X-Nonexistent")
        assert result is None

    def test_extract_from_empty_headers(self):
        """测试从空 headers 提取"""
        result = Extractor.from_header({}, "Content-Type")
        assert result is None


class TestExtractorFromCookie:
    """Cookie 提取测试"""

    def test_extract_existing_cookie(self):
        """测试提取存在的 cookie"""
        cookies = {"session_id": "abc123", "user_id": "1001"}
        result = Extractor.from_cookie(cookies, "session_id")
        assert result == "abc123"

    def test_extract_missing_cookie(self):
        """测试提取不存在的 cookie 返回 None"""
        cookies = {"session_id": "abc123"}
        result = Extractor.from_cookie(cookies, "nonexistent")
        assert result is None

    def test_extract_from_empty_cookies(self):
        """测试从空 cookies 提取"""
        result = Extractor.from_cookie({}, "session_id")
        assert result is None
