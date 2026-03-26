from typing import Sequence, Type, TypedDict

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import BaseChatMessage, ChatMessage, TextMessage
from autogen_core import CancellationToken


class ActorMetadata(TypedDict):
    name: str
    desc: str
    objlol: int


class ClerkAgent(BaseChatAgent):
    def __init__(self, func=None):
        super().__init__(
            "clerk",
            description="书记员，永远不会出场，永远不要选我发言",
        )
        self.conv_func = func or (lambda s: s)
        self._forced_next_speaker: str | None = None

    def set_next_speaker(self, name: str | None) -> None:
        self._forced_next_speaker = name

    def selector(self, messages):
        if self._forced_next_speaker is not None:
            tmp = self._forced_next_speaker
            self._forced_next_speaker = None
            return tmp
        if messages[-1].source != "clerk":
            return "clerk"
        return None

    @property
    def produced_message_types(self) -> Sequence[Type[ChatMessage]]:
        return (TextMessage,)

    async def on_messages(
        self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
    ) -> Response:
        last_message = messages[-1]
        msg = TextMessage(
            content=f"{self.conv_func(last_message.source)} 发言完毕", source=self.name
        )
        return Response(chat_message=msg)

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass
