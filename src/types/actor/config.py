from typing import Annotated, Literal

from pydantic import BaseModel, Field

from src.types.model_config import ModelConfig


class TeamsConfig(BaseModel):
    prosecution: list[str] = Field(alias="prosecution")
    defense: list[str] = Field(alias="defense")
    judge: str = Field(alias="judge")
    judge_final: str = Field(alias="judge_final")
    witness: list[str] = Field(alias="witness")


class StdioMcpServerConfig(BaseModel):
    type: Literal["stdio"] = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    read_timeout_seconds: int = 20


class HttpMcpServerConfig(BaseModel):
    type: Literal["http"] = "http"
    url: str
    headers: dict[str, str] | None = None
    timeout: float = 30.0
    sse_read_timeout: float = 300.0
    terminate_on_close: bool = True


McpServerConfig = Annotated[
    StdioMcpServerConfig | HttpMcpServerConfig,
    Field(discriminator="type"),
]


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
