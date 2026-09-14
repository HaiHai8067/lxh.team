# LXH - Lucid eXtended Harness

> 让测试更灵犀 · 清晰、智能、高度可扩展的自动化测试框架

LXH 是一款基于 pytest 二次开发的企业级自动化测试框架，支持 **API 测试、UI 测试、性能测试** 三大领域，并深度集成 **AI 能力**，让测试更简单、更智能、更高效。

## ✨ 特性

- 🚀 **一键脚手架** - 秒级创建项目，开箱即用
- 🔌 **插件化架构** - 高度可扩展，模块按需加载
- 🔗 **API 测试** - 关键字驱动，HAR 转用例，数据驱动
- 🖥️ **UI 测试** - 基于 Playwright，Page Object，智能等待
- ⚡ **性能测试** - 基于 Locust，分布式压测，实时监控
- 🤖 **AI 赋能** - 用例生成、失败分析、智能断言
- 📊 **精美报告** - Allure / HTML 双报告支持

## 🚀 快速开始

### 安装

```bash
# 基础版（仅 API 测试）
pip install lxh

# 完整版（API + UI + 性能 + AI）
pip install "lxh[full]"
```

### 创建项目

```bash
lxh startproject my_project
cd my_project
```

### 运行测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 指定环境
pytest --env=test
```

## 📁 项目结构

```
my_project/
├── tests/              # 测试用例
├── fixtures/           # 自定义 fixtures
├── data/               # 测试数据
├── reports/            # 测试报告
├── conftest.py         # pytest 配置
├── pytest.ini          # pytest 配置文件
└── README.md
```

## 🧩 模块架构

```
lxh/
├── core/               # 核心框架
├── api/                # API 测试模块
├── ui/                 # UI 测试模块（可选）
├── perf/               # 性能测试模块（可选）
├── ai/                 # AI 智能模块（可选）
├── fixtures/           # 内置 fixtures
└── templates/          # 项目模板
```

## 📄 许可证

MIT License
