"""
项目脚手架模块
负责创建项目结构和模板文件
"""

import click
import shutil
from pathlib import Path


# 基础模板文件（所有项目类型都包含）
BASE_FILES = [
    "tests/__init__.py",
    "tests/test_demo.py",
    "fixtures/__init__.py",
    "fixtures/fixture_sample.py",
    "conftest.py",
    "pytest.ini",
    "env.yaml",
    "gitignore",
    "README.md",
    "data/.gitkeep",
    "reports/.gitkeep",
]

# 按模板类型的额外文件
TEMPLATE_EXTRAS = {
    "api": [
        "tests/test_api_demo.py",
    ],
    "ui": [
        "tests/test_ui_demo.py",
    ],
    "perf": [
        "locustfile.py",
    ],
    "full": [
        "tests/test_api_demo.py",
        "tests/test_ui_demo.py",
        "locustfile.py",
    ],
}

def get_template_dir() -> Path:
    """获取模板目录路径"""
    return Path(__file__).parent.parent / "templates" / "project"

def create_project(project_name: str, template: str = "api", base_path: str = ".") -> bool:
    """
    创建新项目

    Args:
        project_name: 项目名称
        template: 项目类型 (api/ui/perf/full)
        base_path: 基础路径

    Returns:
        是否创建成功
    """
    template_dir = get_template_dir()
    project_path = Path(base_path) / project_name

