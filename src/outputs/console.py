from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import (
    BaseAgentEvent,
    BaseChatMessage,
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

from src.types.agent import AgentMetadata
from src.types.config import AppConfig


class ConsoleFormatter:
    def __init__(self, config: AppConfig, metamap: dict[str, AgentMetadata]) -> None:
        self.config = config
        self.metamap = metamap
        self.console = Console()
        self.status: Status | None = None

    def _get_styling(self, source: str) -> tuple[str, str, str, str]:
        metadata = self.metamap.get(source, {})
        display_name = str(metadata.get("name", source))
        if source in self.config.teams.prosecution:
            return display_name, "[bold blue]", "[/bold blue]", "Prosecution"
        elif source in self.config.teams.defense:
            return display_name, "[bold red]", "[/bold red]", "Defense"
        elif source in self.config.teams.witness:
            return display_name, "[bold purple]", "[/bold purple]", "Witness"
        elif (
            source == self.config.teams.judge or source == self.config.teams.judge_final
        ):
            return display_name, "[bold yellow]", "[/bold yellow]", "Judge"
        return display_name, "[bold yellow]", "[/bold yellow]", "Unknown"

    def _print_panel(
        self,
        content: str,
        source: str,
        subtitle: str = "",
        style: str = "",
        add_status: bool = False,
        status_text: str = "",
    ) -> None:
        if source == "clerk":
            return
        display_name, c_start, c_end, _ = self._get_styling(source)
        self._stop_status()
        self.console.print(
            Panel(
                Markdown(content),
                title=f"{c_start}【{display_name}】{c_end} {subtitle}",
                title_align="left",
                style=style,
            )
        )
        if add_status:
            self.status = self.console.status(
                f"{c_start}【{display_name}】{c_end} {status_text}"
            )
            self.status.start()

    def print_system(self, text: str) -> None:
        self.console.rule(f"[bold] === {text} === [/bold]")

    def print_event(
        self,
        event: BaseAgentEvent | BaseChatMessage | TaskResult,
    ) -> None:
        match event:
            case ModelClientStreamingChunkEvent():
                return

            case SelectSpeakerEvent():
                self._print_panel(
                    "申请发言！",
                    event.content[0],
                    "（举手）",
                    "italic bright_black",
                    add_status=True,
                    status_text="正在思考...",
                )

            case TextMessage():
                self._print_panel(
                    event.content,
                    event.source,
                )

            case ThoughtEvent():
                source = getattr(event, "source", "Unknown") or "System"
                self._print_panel(
                    event.content,
                    source,
                    "（思考中）",
                    "italic bright_black",
                )

            case ToolCallRequestEvent():
                source = getattr(event, "source", "Unknown") or "System"
                self._print_panel(
                    "调用了：\n"
                    + "\n".join(
                        [f"- {call.name}: {call.arguments}" for call in event.content]
                    ),
                    source,
                    "（查阅资料中）",
                    "italic bright_black",
                )

            case ToolCallExecutionEvent():
                source = getattr(event, "source", "Unknown") or "System"
                self._print_panel(
                    "...",
                    source,
                    "（资料查阅完毕）",
                    "italic bright_black",
                    add_status=True,
                    status_text=" 正在组织语言...",
                )

            case _:
                return

    def _stop_status(self) -> None:
        if self.status:
            self.status.stop()
            self.status = None
