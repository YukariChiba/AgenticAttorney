import json
from uuid import uuid4

from autogen_agentchat.messages import (
    TextMessage,
)

from src.constants import LOGS_DIR
from src.types.actor.agent import ActorMetadata
from src.types.config import AppConfig
from src.types.logfile import LogEntry


class LogfileFormatter:
    def __init__(self, config: AppConfig, metamap: dict[str, ActorMetadata]) -> None:
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
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        savefile = LOGS_DIR / f"{uuid4()}.json"
        with open(savefile, "w", encoding="utf-8") as f:
            json.dump(self.fulllog, f, indent=4, ensure_ascii=False)
        return str(savefile)

    def _get_character_type(self, source: str) -> str:
        if source in self.config.actor.teams.prosecution:
            return "Prosecution"
        elif source in self.config.actor.teams.defense:
            return "Defense"
        elif source in self.config.actor.teams.witness:
            return "Witness"
        elif (
            source == self.config.actor.teams.judge
            or source == self.config.actor.teams.judge_final
        ):
            return "Judge"
        return "Unknown"
