from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lxh",
    version="0.1.0",
    author="LXH Team",
    author_email="team@lxh.dev",
    description="LXH - Lucid eXtended Harness, 一个清晰、智能、高度可扩展的自动化测试框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lxh-framework/lxh",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "lxh": ["templates/project/**/*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pytest>=7.4.0",
        "click>=8.1.0",
        "PyYAML>=6.0",
        "loguru>=0.7.0",
        "requests>=2.31.0",
        "jsonpath-ng>=1.5.3",
        "allure-pytest>=2.13.0",
    ],
    extras_require={
        "ui": ["playwright>=1.40.0"],
        "perf": ["locust>=2.17.0"],
        "ai": ["openai>=1.0.0"],
        "full": [
            "playwright>=1.40.0",
            "locust>=2.17.0",
            "openai>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lxh=lxh.cli:cli",
        ],
        "pytest11": [
            "lxh=lxh.plugin",
        ],
    },
)
