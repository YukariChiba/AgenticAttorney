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
    summary_context: int = 10


class McpServerConfig(BaseModel):
    type: str = "stdio"
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] | None = None
    read_timeout_seconds: int = 20
