from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="hypurrscan-monitor",
    version="0.1.0",
    author="BugSmith",
    author_email="your.email@example.com",
    description="一个监控hypurrscan.io交易所仓位变化的Telegram机器人",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BugSmith/Hypurrscan_Monitor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hypurrscan-monitor=main:main",
        ],
    },
) 