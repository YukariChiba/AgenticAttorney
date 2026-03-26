"""配置加载器 - 处理所有与文件 I/O 相关的配置加载逻辑"""

import json
from pathlib import Path

import frontmatter

from src.constants import TOPICS_DIR
from src.types.config import AppConfig


def load_config(config_path: str | Path = "config.json") -> AppConfig:
    if isinstance(config_path, str):
        config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config文件不存在: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        return AppConfig.model_validate(json.load(f))


def load_topic_md(topic_name: str) -> frontmatter.Post:
    topic_file = TOPICS_DIR / f"{topic_name}.md"
    if not topic_file.exists():
        raise FileNotFoundError(f"主题文件不存在: {topic_file}")
    with open(topic_file, encoding="utf-8") as f:
        return frontmatter.load(f)
