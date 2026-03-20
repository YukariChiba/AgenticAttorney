import json
import os
from uuid import uuid4

from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import (
    BaseAgentEvent,
    BaseChatMessage,
    MemoryQueryEvent,
    ModelClientStreamingChunkEvent,
    SelectSpeakerEvent,
    TextMessage,
    ThoughtEvent,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
)
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status

from config import teams


class Formatter:
    namemap: dict[str, str]
    console: Console
    status: Status | None
    fulllog: list[tuple[str, str]]

    def __init__(self, namemap: dict[str, str] | None = None) -> None:
        self.namemap = namemap if namemap is not None else {}
        self.console = Console()
        self.status = None
        self.fulllog = []

    def _get_styling(self, source: str) -> tuple[str, str, str]:
        display_name: str = self.namemap.get(source, source)
        if source in teams.A:
            return display_name, "[bold blue]", "[/bold blue]"
        elif source in teams.N:
            return display_name, "[bold red]", "[/bold red]"
        elif source in teams.W:
            return display_name, "[bold purple]", "[/bold purple]"
        return display_name, "[bold yellow]", "[/bold yellow]"

    def savelog(self, filename=uuid4()):
        os.makedirs("logs", exist_ok=True)
        savefile = f"logs/{filename}.json"
        with open(savefile, "w", encoding="utf-8") as f:
            json.dump(self.fulllog, f, indent=4, ensure_ascii=False)
        return savefile

    def fmtsys(self, text):
        self.console.rule(
            f"[bold] === {text} === [/bold]",
        )

    def fmtmsg(self, event: BaseAgentEvent | BaseChatMessage | TaskResult):
        if not isinstance(
            event,
            TextMessage
            | ThoughtEvent
            | ToolCallRequestEvent
            | MemoryQueryEvent
            | SelectSpeakerEvent
            | ModelClientStreamingChunkEvent
            | ToolCallExecutionEvent,
        ):
            return
        source: str = getattr(event, "source", "Unknown") or "System"
        if isinstance(event, SelectSpeakerEvent):
            source = event.content[0]
        display_name, c_start, c_end = self._get_styling(source)
        title_prefix = f"{c_start}【{display_name}】{c_end}"

        if isinstance(event, ModelClientStreamingChunkEvent):
            return  # WIP

        if self.status:
            self.status.stop()
            self.status = None

        if isinstance(event, TextMessage):
            self.console.print(
                Panel(
                    Markdown(event.content),
                    title=title_prefix,
                    title_align="left",
                )
            )
            self.fulllog.append((f"{display_name} ({source})", event.content))
        if isinstance(event, ThoughtEvent):
            self.console.print(
                Panel(
                    Markdown(event.content),
                    title=f"{title_prefix} （思考中）",
                    title_align="left",
                    style="italic bright_black",
                )
            )
        if isinstance(event, SelectSpeakerEvent):
            if teams.JR and source in teams.JR:
                # 陪审团不需要申请发言
                return
            self.console.print(
                Panel(
                    "申请发言！",
                    title=f"{title_prefix} （举手）",
                    title_align="left",
                    style="italic bright_black",
                )
            )
            self.status = self.console.status(f"{title_prefix} 正在思考...")
            self.status.start()
        if isinstance(event, MemoryQueryEvent):
            self.console.print(
                Panel(
                    "...",
                    title=f"{title_prefix} （翻看材料中）",
                    title_align="left",
                    style="italic bright_black",
                )
            )
        if isinstance(event, ToolCallRequestEvent):
            self.console.print(
                Panel(
                    "调用了：\n"
                    + "\n".join(
                        [f"- {call.name}: {call.arguments}" for call in event.content]
                    ),
                    title=f"{title_prefix} （查阅资料中）",
                    title_align="left",
                    style="italic bright_black",
                )
            )
        if isinstance(event, ToolCallExecutionEvent):
            self.console.print(
                Panel(
                    "...",
                    title=f"{title_prefix} （资料查阅完毕）",
                    title_align="left",
                    style="italic bright_black",
                )
            )
            self.status = self.console.status(f"{title_prefix} 正在组织语言...")
            self.status.start()
