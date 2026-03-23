import json
import os
from uuid import uuid4

from autogen_agentchat.messages import (
    TextMessage,
)

from src.agents.manager import AgentMetadata
from src.core.models import AppConfig
from src.types.logger import LogEntry


class DebateLogger:
    def __init__(self, config: AppConfig, metamap: dict[str, AgentMetadata]) -> None:
        self.config = config
        self.metamap = metamap
        self.fulllog: list[LogEntry] = []

    def log_event(self, event: TextMessage) -> None:
        source = event.source
        if event.source == "clerk":
            return
        metadata = self.metamap.get(source, {})
        name = str(metadata.get("name", source))
        objlol_id = int(metadata.get("objlol", 0))
        role = self._get_character_type(source)
        self.fulllog.append(
            LogEntry(name=name, objlol_id=objlol_id, role=role, content=event.content)
        )

    def save(self) -> str:
        os.makedirs("logs", exist_ok=True)
        savefile = f"logs/{uuid4()}.json"
        with open(savefile, "w", encoding="utf-8") as f:
            json.dump(self.fulllog, f, indent=4, ensure_ascii=False)
        return savefile

    def _get_character_type(self, source: str) -> str:
        if source in self.config.teams.prosecution:
            return "Prosecution"
        elif source in self.config.teams.defense:
            return "Defense"
        elif source in self.config.teams.witness:
            return "Witness"
        elif self.config.teams.jury and source in self.config.teams.jury:
            return "Jury"
        elif source in self.config.teams.judge:
            return "Judge"
        elif source in self.config.teams.judge_final:
            return "Judge"
        return "Unknown"
