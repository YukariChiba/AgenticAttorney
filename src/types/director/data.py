import base64
import json
import uuid

from pydantic import BaseModel


class Options(BaseModel):
    chatbox: str = "0"
    textSpeed: int = 50
    textBlipFrequency: int = 64
    autoplaySpeed: int = 500
    continueSoundUrl: str = ""


class CourtRecord(BaseModel):
    evidence: list = []
    profiles: list = []


class Group(BaseModel):
    id: str
    type: str = "normal"
    name: str = "Main"
    frames: list[dict]
    comments: dict = {}


class DirectorData(BaseModel):
    id: str
    type: str = "scene"
    options: Options
    courtRecord: CourtRecord
    aliases: list = []
    pairs: list = []
    groups: list[Group]
    nextFrameId: int
    freeFrameIds: list = []
    version: int = 5

    @classmethod
    def from_frames(cls, frames: list[dict]) -> "DirectorData":
        return cls(
            id=str(uuid.uuid4()),
            options=Options(),
            courtRecord=CourtRecord(),
            groups=[
                Group(
                    id=str(uuid.uuid4()),
                    frames=frames,
                )
            ],
            nextFrameId=len(frames) + 1,
        )

    def to_base64(self) -> bytes:
        json_data = json.dumps(
            self.model_dump(mode="python"), ensure_ascii=False, indent=2
        ).encode("utf-8")
        return base64.b64encode(json_data)

    def to_file(self, output_path: str) -> None:
        with open(output_path, "wb") as f:
            f.write(self.to_base64())
