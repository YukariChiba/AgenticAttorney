import datetime

import frontmatter
from dateutil.tz import tzlocal

from src.prompts.engine import TemplateEngine


class DebateTemplateEngine(TemplateEngine):
    def load_and_render(
        self, filepath: str, data: dict[str, str | int] | None = None
    ) -> frontmatter.Post:
        stance = data.get("stance") if data else None
        rdata: dict[str, str | int] = {
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
            rdata["affirmative_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/prosecution/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.prosecution
                ]
            )
        if self.config.teams.defense:
            rdata["negative_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/defense/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.defense
                ]
            )
        if self.config.teams.witness:
            rdata["witness_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/witness/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.teams.witness
                ]
            )
        if data:
            rdata.update(data)

        return super().load_and_render(filepath, rdata)
