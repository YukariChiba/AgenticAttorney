from pydantic import BaseModel, Field

from src.types.model_config import ModelConfig


class TeamsConfig(BaseModel):
    prosecution: list[str] = Field(alias="prosecution")
    defense: list[str] = Field(alias="defense")
    judge: str = Field(alias="judge")
    judge_final: str = Field(alias="judge_final")
    witness: list[str] = Field(alias="witness")


class McpServerConfig(BaseModel):
    type: str = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    read_timeout_seconds: int = 20


class ActorConfig(BaseModel):
    model: ModelConfig
    topic: str
    teams: TeamsConfig
    mcp_servers: list[McpServerConfig] = Field(default_factory=list)
    max_words: int = 300
    max_rounds: int = 20
    max_context: int = 16
    summary_start: int = 4
    summary_end: int = 4
    max_tool_iterations: int = 5
    prepare: bool = True
