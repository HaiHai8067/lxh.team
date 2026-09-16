"""
环境配置管理模块
支持多环境配置、YAML 文件、环境变量覆盖
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None


class EnvConfig:
    """环境配置管理器"""

    def __init__(self, env:str = "test", config_path: Optional[str] = None, root_dir: Optional[str] = None):
        """
        初始化环境配置

        Args:
            env: 环境名称 (dev/test/staging/prod)
            config_path: 配置文件路径
            root_dir: 项目根目录
        """
        self.env = env
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.config_path = Path(config_path) if config_path else self.root_dir / "env.yaml"
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """加载配置文件"""
        if not self.config_path.exists():
            return

        if yaml is None:
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if self.env in data:
                self._config = data[self.env] or {}
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键，支持点分隔的嵌套路径，如 "database.host"
            default: 默认值
        """
        keys = key.split(".")
        current = self._config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current
    def __getitem__(self, key: str) -> Any:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    @property
    def all(self) -> Dict[str, Any]:
        """获取全部配置"""
        return self._config.copy()

    def __repr__(self) -> str:
        return f"EnvConfig(env='{self.env}', keys={list(self._config.keys())})"


_global_config: Optional[EnvConfig] = None


def get_env_config(env: str = "test", config_path: Optional[str] = None, root_dir: Optional[str] = None) -> EnvConfig:
    """获取全局环境配置实例（单例模式）"""
    global _global_config

    if _global_config is None or _global_config.env != env:
        _global_config = EnvConfig(env, config_path, root_dir)

    return _global_config
