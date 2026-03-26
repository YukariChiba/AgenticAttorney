from pydantic import BaseModel

from src.types.model_config import ModelConfig


class DirectorConfig(BaseModel):
    model: ModelConfig
    buffer_size: int = 3
    max_retries: int = 3
    cache_duration: int = 86400
