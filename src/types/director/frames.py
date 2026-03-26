from typing import Annotated, Optional

from pydantic import BaseModel, RootModel


class Frame(BaseModel):
    character: Annotated[int, "角色的 ID"]
    content: Annotated[str, "角色的思考或发言"]
    pose: Annotated[int, "角色姿势的 ID，从角色可用姿势中选择"]
    bubble: Annotated[Optional[int], "可选，角色气泡的 ID，从角色可用气泡中选择"] = None
    talk: Annotated[
        bool, "角色是否在说话，默认为是，如果角色只在思考/内心独白，就设置为否"
    ] = True


class FrameList(RootModel):
    root: list[Frame]


class DirectorFrame(BaseModel):
    id: int
    characterId: int
    text: str
    poseId: int
    speechBubble: Optional[int] = None
    backgroundId: Optional[int] = None
    flipped: Optional[int] = None
    moveToNext: bool = True
    talk: bool = True

    @classmethod
    def from_frame(
        cls,
        frame: Frame,
        bg_id: Optional[int],
        frame_id: int,
    ) -> "DirectorFrame":
        return DirectorFrame(
            id=frame_id,
            characterId=frame.character,
            text=frame.content,
            poseId=frame.pose,
            speechBubble=frame.bubble,
            backgroundId=bg_id,
            flipped=None,
            moveToNext=False,
            talk=frame.talk,
        )

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "characterId": self.characterId,
            "text": self.text,
            "poseId": self.poseId,
            "moveToNext": self.moveToNext,
        }
        if self.speechBubble is not None:
            result["speechBubble"] = self.speechBubble
        if self.backgroundId is not None:
            result["backgroundId"] = self.backgroundId
        if self.flipped is not None:
            result["flipped"] = self.flipped
        return result
