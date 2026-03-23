from pathlib import Path
from typing import Any

import frontmatter
from pydantic import BaseModel, Field

from src.types.config import (
    DebateSettingsConfig,
    McpServerConfig,
    ModelInfo,
    TeamsConfig,
)


class ModelConfig(BaseModel):
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    timeout: int = 1200
    temperature: float = 0.9
    parallel_tool_calls: bool = True
    model_info: ModelInfo

    def to_component_config(self) -> dict[str, Any]:
        config_dict = {
            "provider": self.provider,
            "config": {
                "model": self.model,
                "timeout": self.timeout,
                "temperature": self.temperature,
                "parallel_tool_calls": self.parallel_tool_calls,
            },
        }
        if self.base_url:
            config_dict["config"]["base_url"] = self.base_url
        if self.api_key:
            config_dict["config"]["api_key"] = self.api_key
        if self.model_info:
            config_dict["config"]["model_info"] = (
                dict(self.model_info)
                if hasattr(self.model_info, "model_dump")
                else self.model_info
            )
        return config_dict


class AppConfig(BaseModel):
    model: ModelConfig
    topic: str
    teams: TeamsConfig
    debate: DebateSettingsConfig
    mcp_servers: list[McpServerConfig] = Field(default_factory=list)

    @classmethod
    def load(cls, config_path: str | Path = "config.json") -> "AppConfig":
        if isinstance(config_path, str):
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config文件不存在: {config_path}")

        import json

        with open(config_path, encoding="utf-8") as f:
            return cls.model_validate(json.load(f))

    @property
    def topic_md(self) -> frontmatter.Post:
        topic_file = Path("prompts/topics") / f"{self.topic}.md"
        if not topic_file.exists():
            raise FileNotFoundError(f"主题文件不存在: {topic_file}")
        with open(topic_file, encoding="utf-8") as f:
            return frontmatter.load(f)

    @property
    def debate_topic(self) -> str:
        return str(self.topic_md.metadata.get("debate_topic", ""))

    @property
    def debate_topic_full(self) -> str:
        return self.topic_md.content

    @property
    def affirmative_stance(self) -> str:
        return str(self.topic_md.metadata.get("affirmative_stance", ""))

    @property
    def negative_stance(self) -> str:
        return str(self.topic_md.metadata.get("negative_stance", ""))
