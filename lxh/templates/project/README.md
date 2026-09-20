# {project_name}

基于 LXH 框架的自动化测试项目

> 模板类型: {template}

## 快速开始

### 安装依赖

```bash
pip install lxh
```

### 运行测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 指定运行环境
pytest --env=test

# 运行指定文件
pytest tests/test_demo.py

# 运行指定用例
pytest tests/test_demo.py::test_lxh_basic
```

## 项目结构

```
{project_name}/
├── tests/              # 测试用例目录
│   ├── __init__.py
│   └── test_demo.py    # 示例用例
├── fixtures/           # 自定义 fixtures（自动加载）
│   ├── __init__.py
│   └── fixture_sample.py
├── data/               # 测试数据
├── reports/            # 测试报告
├── conftest.py         # pytest 全局配置
├── pytest.ini          # pytest 配置文件
└── README.md
```

## 内置 Fixtures

| Fixture 名称 | 作用域 | 说明 |
|-------------|--------|------|
| lxh_env | session | 当前运行环境名称 |
| lxh_config | session | 环境配置对象 |
| lxh_project_root | session | 项目根目录路径 |
| lxh_tests_dir | session | tests 目录路径 |
| lxh_data_dir | session | data 目录路径 |
| lxh_reports_dir | session | reports 目录路径 |
| lxh_vars | function | 用例级变量存储 |
| lxh_module_vars | module | 模块级变量存储 |
| lxh_logger | function | 用例级 logger |

## 环境配置

在项目根目录创建 `env.yaml`：

```yaml
dev:
  base_url: http://dev.example.com
  username: dev_user

test:
  base_url: http://test.example.com
  username: test_user

prod:
  base_url: http://api.example.com
  username: prod_user
```

运行时指定环境：

```bash
pytest --env=test
```

## 自定义 Fixtures

在 `fixtures/` 目录下创建 `fixture_*.py` 文件，框架会自动加载。

```python
# fixtures/fixture_my.py
import pytest

@pytest.fixture
def my_data():
    return {"key": "value"}
```

---

**LXH - Lucid eXtended Harness · 让测试更灵犀**
