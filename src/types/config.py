import json
from pathlib import Path
from typing import Any

import frontmatter
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    vision: bool = False
    function_calling: bool = True
    json_output: bool = True
    family: str = "unknown"
    structured_output: bool = True


class TeamsConfig(BaseModel):
    prosecution: list[str] = Field(alias="prosecution")
    defense: list[str] = Field(alias="defense")
    judge: str = Field(alias="judge")
    judge_final: str = Field(alias="judge_final")
    witness: list[str] = Field(alias="witness")


class DebateSettingsConfig(BaseModel):
    max_words: int = 300
    max_rounds: int = 20
    max_context: int = 16
    summary_start: int = 4
    summary_end: int = 4
    max_tool_iterations: int = 5


class McpServerConfig(BaseModel):
    type: str = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    read_timeout_seconds: int = 20


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
            config_dict["config"]["model_info"] = self.model_info.model_dump()
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
