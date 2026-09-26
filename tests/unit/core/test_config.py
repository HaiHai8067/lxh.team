"""
环境配置模块单元测试
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from lxh.core.config import EnvConfig, get_env_config


@pytest.fixture
def temp_config_file():
    """创建临时配置文件"""
    config_data = {
        "dev": {
            "base_url": "http://dev.example.com",
            "database": {
                "host": "localhost",
                "port": 3306,
            },
            "headers": {
                "X-Env": "dev",
            },
        },
        "test": {
            "base_url": "http://test.example.com",
            "database": {
                "host": "test-db.example.com",
                "port": 3307,
            },
        },
        "prod": {
            "base_url": "https://api.example.com",
        },
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(config_data, f)
        config_path = f.name

    yield Path(config_path)

    os.unlink(config_path)


class TestEnvConfig:
    """EnvConfig 测试类"""

    def test_init_with_existing_config(self, temp_config_file):
        """测试使用存在的配置文件初始化"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert config.env == "test"
        assert "base_url" in config.all

    def test_init_with_nonexistent_config(self):
        """测试使用不存在的配置文件初始化"""
        config = EnvConfig(env="test", config_path="/nonexistent/path.yaml")
        assert config.env == "test"
        assert config.all == {}

    def test_get_simple_key(self, temp_config_file):
        """测试获取简单键"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert config.get("base_url") == "http://test.example.com"

    def test_get_nested_key(self, temp_config_file):
        """测试获取嵌套键（点分隔）"""
        config = EnvConfig(env="dev", config_path=str(temp_config_file))
        assert config.get("database.host") == "localhost"
        assert config.get("database.port") == 3306

    def test_get_deeply_nested_key(self, temp_config_file):
        """测试获取深层嵌套键"""
        config = EnvConfig(env="dev", config_path=str(temp_config_file))
        assert config.get("headers.X-Env") == "dev"

    def test_get_with_default(self, temp_config_file):
        """测试获取不存在的键时返回默认值"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert config.get("nonexistent_key", "default") == "default"
        assert config.get("database.nonexistent", 0) == 0

    def test_get_none_value(self, temp_config_file):
        """测试获取值为 None 的情况"""
        config = EnvConfig(env="prod", config_path=str(temp_config_file))
        assert config.get("database") is None

    def test_getitem_existing(self, temp_config_file):
        """测试 __getitem__ 访问存在的键"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert config["base_url"] == "http://test.example.com"

    def test_getitem_nonexistent(self, temp_config_file):
        """测试 __getitem__ 访问不存在的键抛出异常"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        with pytest.raises(KeyError):
            _ = config["nonexistent"]

    def test_contains_existing(self, temp_config_file):
        """测试 __contains__ 检查存在的键"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert "base_url" in config
        assert "database.host" in config

    def test_contains_nonexistent(self, temp_config_file):
        """测试 __contains__ 检查不存在的键"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        assert "nonexistent" not in config
        assert "database.nonexistent" not in config

    def test_all_property(self, temp_config_file):
        """测试 all 属性返回完整配置"""
        config = EnvConfig(env="dev", config_path=str(temp_config_file))
        all_config = config.all
        assert isinstance(all_config, dict)
        assert "base_url" in all_config
        assert "database" in all_config
        # 确保返回的是副本，不会影响原配置
        all_config["new_key"] = "test"
        assert "new_key" not in config.all

    def test_different_environments(self, temp_config_file):
        """测试不同环境返回不同配置"""
        dev_config = EnvConfig(env="dev", config_path=str(temp_config_file))
        test_config = EnvConfig(env="test", config_path=str(temp_config_file))
        prod_config = EnvConfig(env="prod", config_path=str(temp_config_file))

        assert dev_config.get("base_url") == "http://dev.example.com"
        assert test_config.get("base_url") == "http://test.example.com"
        assert prod_config.get("base_url") == "https://api.example.com"

    def test_repr(self, temp_config_file):
        """测试 __repr__ 方法"""
        config = EnvConfig(env="test", config_path=str(temp_config_file))
        repr_str = repr(config)
        assert "test" in repr_str
        assert "EnvConfig" in repr_str

    def test_empty_env_in_config(self, temp_config_file):
        """测试环境在配置中但配置为空"""
        # 创建一个有 staging 但为空的配置
        config_data = {"staging": None}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(config_data, f)
            path = f.name

        try:
            config = EnvConfig(env="staging", config_path=path)
            assert config.all == {}
        finally:
            os.unlink(path)

    def test_root_dir_parameter(self):
        """测试 root_dir 参数"""
        config = EnvConfig(env="test", root_dir="/tmp")
        assert config.root_dir == Path("/tmp")


class TestGetEnvConfig:
    """get_env_config 单例函数测试"""

    def test_returns_same_instance_for_same_env(self, temp_config_file):
        """测试相同环境返回同一个实例"""
        config1 = get_env_config(env="test", config_path=str(temp_config_file))
        config2 = get_env_config(env="test", config_path=str(temp_config_file))
        assert config1 is config2

    def test_returns_different_instance_for_different_env(self, temp_config_file):
        """测试不同环境返回不同实例"""
        config1 = get_env_config(env="dev", config_path=str(temp_config_file))
        config2 = get_env_config(env="test", config_path=str(temp_config_file))
        assert config1 is not config2

    def test_env_change_creates_new_instance(self, temp_config_file):
        """测试环境切换后创建新实例"""
        # 先创建 dev 环境实例
        get_env_config(env="dev", config_path=str(temp_config_file))
        # 切换到 test 环境（创建新实例）
        config2 = get_env_config(env="test", config_path=str(temp_config_file))
        # 切回 dev 环境（再次创建新实例）
        config3 = get_env_config(env="dev", config_path=str(temp_config_file))
        # 切回 dev 时，因为之前 test 环境创建了新实例，dev 实例已被替换
        assert config2 is not config3
        assert config3.env == "dev"
