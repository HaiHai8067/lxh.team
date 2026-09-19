"""
LXH CLI 命令行入口
基于 click 实现命令行工具
"""

import click
from lxh import __version__, __slogan__


@click.group(help=f"LXH - Lucid eXtended Harness\n{__slogan__}")
@click.version_option(version=__version__, prog_name="lxh")
def cli():
    """LXH 命令行工具"""
    pass


@cli.command()
@click.argument("project_name")
@click.option(
    "--template", "-t",
    type=click.Choice(["api", "ui", "perf", "full"], case_sensitive=False),
    default="api",
    help="项目模板类型: api/ui/perf/full，默认 api"
)
@click.option(
    "--path", "-p",
    default=".",
    help="项目创建路径，默认为当前目录"
)
def startproject(project_name, template, path):
    """创建新项目脚手架

    PROJECT_NAME: 项目名称
    """
    from lxh.core.scaffold import create_project
    create_project(project_name, template, path)


@cli.command()
def info():
    """显示框架信息"""
    click.echo()
    click.echo(f"  ⚡ LXH - Lucid eXtended Harness")
    click.echo(f"  {__slogan__}")
    click.echo()
    click.echo(f"  版本: {__version__}")
    click.echo()
    click.echo("  常用命令:")
    click.echo("    lxh startproject <项目名>   创建新项目")
    click.echo("    lxh info                   显示框架信息")
    click.echo("    pytest                     运行测试用例")
    click.echo()
    click.echo("  项目模板:")
    click.echo("    --template=api     API 自动化测试项目")
    click.echo("    --template=ui      UI 自动化测试项目")
    click.echo("    --template=perf    性能测试项目")
    click.echo("    --template=full    全栈测试项目（API+UI+性能）")
    click.echo()


def main():
    cli()


if __name__ == "__main__":
    main()
