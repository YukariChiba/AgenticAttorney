from typing import Optional

from pydantic import BaseModel


class Music(BaseModel):
    name: str
    id: int


class Sound(BaseModel):
    name: str
    id: int


class Character(BaseModel):
    id: int
    name: str
    side: Optional[str] = None
    backgroundId: Optional[int] = None
    poses: dict[str, int]
    speechBubbles: dict[str, int]
