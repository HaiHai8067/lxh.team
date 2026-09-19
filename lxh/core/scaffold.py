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

    # 检查项目是否已存在
    if project_path.exists():
        click.echo(f"❌ 错误: 目录 '{project_name}' 已存在！", err=True)
        return False

    # 创建项目根目录
    project_path.mkdir(parents=True, exist_ok=True)
    click.echo()
    click.echo(f"📁 创建项目: {project_name}/")
    click.echo(f"   模板类型: {template}")
    click.echo()

    # 确定需要复制的文件列表
    files_to_copy = list(BASE_FILES)
    if template in TEMPLATE_EXTRAS:
        files_to_copy.extend(TEMPLATE_EXTRAS[template])

    # 复制文件
    created_count = 0
    for rel_path in files_to_copy:
        src_path = template_dir / rel_path
        dst_path = project_path / rel_path

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if src_path.exists():
            content = _render_template(src_path, project_name, template)
            dst_path.write_text(content, encoding="utf-8")
            created_count += 1
            click.echo(f"  ✅ {rel_path}")
        elif rel_path.endswith(".gitkeep"):
            # .gitkeep 文件直接创建
            dst_path.touch()
            created_count += 1
        else:
            click.echo(f"  ⚠️  跳过缺失模板: {rel_path}")

    click.echo()
    click.echo(f"🎉 项目 '{project_name}' 创建成功！共创建 {created_count} 个文件")
    click.echo()
    click.echo("🚀 快速开始:")
    click.echo(f"  cd {project_name}")
    click.echo(f"  pytest -v")
    click.echo()

    return True


def _render_template(src_path: Path, project_name: str, template: str) -> str:
    """
    渲染模板文件

    Args:
        src_path: 源文件路径
        project_name: 项目名称
        template: 模板类型

    Returns:
        渲染后的内容
    """
    content = src_path.read_text(encoding="utf-8")
    content = content.replace("{project_name}", project_name)
    content = content.replace("{template}", template)
    content = content.replace("{year}", "2026")
    return content

