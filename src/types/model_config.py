from typing import Any

from pydantic import BaseModel


class ModelInfo(BaseModel):
    vision: bool = False
    function_calling: bool = True
    json_output: bool = True
    family: str = "unknown"
    structured_output: bool = True


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
