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

from src.agents.manager import AgentMetadata
from src.core.models import AppConfig


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
        elif source in self.config.teams.judge:
            return display_name, "[bold yellow]", "[/bold yellow]", "Judge"
        elif source in self.config.teams.judge_final:
            return display_name, "[bold yellow]", "[/bold yellow]", "Judge"
        return display_name, "[bold yellow]", "[/bold yellow]", "Unknown"

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
                source = event.content[0]
                if source == "clerk":
                    return
                display_name, c_start, c_end, char_type = self._get_styling(source)
                self.console.print(
                    Panel(
                        "申请发言！",
                        title=f"{c_start}【{display_name}】{c_end} （举手）",
                        title_align="left",
                        style="italic bright_black",
                    )
                )
                if self.status:
                    self.status.stop()
                self.status = self.console.status(
                    f"{c_start}【{display_name}】{c_end} 正在思考..."
                )
                self.status.start()

            case TextMessage():
                source = event.source
                if source == "clerk":
                    return
                display_name, c_start, c_end, _ = self._get_styling(source)
                self._stop_status()
                self.console.print(
                    Panel(
                        Markdown(event.content),
                        title=f"{c_start}【{display_name}】{c_end}",
                        title_align="left",
                    )
                )

            case ThoughtEvent():
                source = getattr(event, "source", "Unknown") or "System"
                display_name, c_start, c_end, _ = self._get_styling(source)
                self._stop_status()
                self.console.print(
                    Panel(
                        Markdown(event.content),
                        title=f"{c_start}【{display_name}】{c_end} （思考中）",
                        title_align="left",
                        style="italic bright_black",
                    )
                )

            case MemoryQueryEvent():
                source = getattr(event, "source", "Unknown") or "System"
                display_name, c_start, c_end, _ = self._get_styling(source)
                self._stop_status()
                self.console.print(
                    Panel(
                        "...",
                        title=f"{c_start}【{display_name}】{c_end} （翻看材料中）",
                        title_align="left",
                        style="italic bright_black",
                    )
                )

            case ToolCallRequestEvent():
                source = getattr(event, "source", "Unknown") or "System"
                display_name, c_start, c_end, _ = self._get_styling(source)
                self._stop_status()
                self.console.print(
                    Panel(
                        "调用了：\n"
                        + "\n".join(
                            [
                                f"- {call.name}: {call.arguments}"
                                for call in event.content
                            ]
                        ),
                        title=f"{c_start}【{display_name}】{c_end} （查阅资料中）",
                        title_align="left",
                        style="italic bright_black",
                    )
                )

            case ToolCallExecutionEvent():
                source = getattr(event, "source", "Unknown") or "System"
                display_name, c_start, c_end, _ = self._get_styling(source)
                self._stop_status()
                self.console.print(
                    Panel(
                        "...",
                        title=f"{c_start}【{display_name}】{c_end} （资料查阅完毕）",
                        title_align="left",
                        style="italic bright_black",
                    )
                )
                self.status = self.console.status(
                    f"{c_start}【{display_name}】{c_end} 正在组织语言..."
                )
                self.status.start()

            case _:
                return

    def _stop_status(self) -> None:
        if self.status:
            self.status.stop()
            self.status = None
