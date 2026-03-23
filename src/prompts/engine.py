import chevron
import datetime
from pathlib import Path

import frontmatter
from dateutil.tz import tzlocal

from src.core.models import AppConfig


class TemplateEngine:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.prompts_dir = Path("prompts")

    def _load_raw_content(self, filepath: str) -> str:
        full_path = self.prompts_dir / f"{filepath}.md"
        if not full_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {full_path}")
        with open(full_path, encoding="utf-8") as f:
            return f.read()

    def _load_frontmatter(self, filepath: str) -> dict[str, object]:
        content = self._load_raw_content(filepath)
        post = frontmatter.loads(content)
        return post.metadata

    def load_and_render(
        self, filepath: str, extra_context: dict[str, str | int] | None = None
    ) -> frontmatter.Post:
        stance = extra_context.get("stance") if extra_context else None

        content = self._load_raw_content(filepath)

        data: dict[str, str | int] = {
            "stance": stance or self.config.affirmative_stance,
            "affirmative_stance": self.config.affirmative_stance,
            "negative_stance": self.config.negative_stance,
            "debate_topic": self.config.debate_topic,
            "debate_topic_full": self.config.debate_topic_full,
            "max_words": self.config.debate.max_words,
            "max_rounds": self.config.debate.max_rounds,
            "current_date": datetime.datetime.now(tzlocal()).strftime(
                "%Y 年 %m 月 %d 日，%H:%M"
            ),
        }

        if self.config.teams.prosecution:
            data["affirmative_agents"] = ", ".join(
                [
                    f"{self._load_frontmatter('agents/prosecution/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.prosecution
                ]
            )

        if self.config.teams.defense:
            data["negative_agents"] = ", ".join(
                [
                    f"{self._load_frontmatter('agents/defense/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.defense
                ]
            )

        if self.config.teams.witness:
            data["witness_agents"] = ", ".join(
                [
                    f"{self._load_frontmatter('agents/witness/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.witness
                ]
            )

        if extra_context:
            data.update(extra_context)

        content = chevron.render(content, data)

        return frontmatter.loads(content)

    def load_content(self, filepath: str) -> str:
        return self.load_and_render(filepath).content

    def load_metadata(self, filepath: str) -> dict[str, object]:
        return self.load_and_render(filepath).metadata
