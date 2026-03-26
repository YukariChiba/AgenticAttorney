from pydantic import BaseModel

from src.types.actor.config import ActorConfig
from src.types.director.config import DirectorConfig


class AppConfig(BaseModel):
    actor: ActorConfig
    director: DirectorConfig
