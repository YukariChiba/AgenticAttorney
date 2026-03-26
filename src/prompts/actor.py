import datetime

import frontmatter
from dateutil.tz import tzlocal

from src.core.config_loader import load_topic_md
from src.prompts.engine import TemplateEngine


class ActorTemplateEngine(TemplateEngine):
    def load_and_render(
        self, filepath: str, data: dict[str, str | int] | None = None
    ) -> frontmatter.Post:
        topic_md = load_topic_md(self.config.actor.topic)

        stance = data.get("stance") if data else None
        affirmative_stance = str(topic_md.metadata.get("affirmative_stance", ""))
        negative_stance = str(topic_md.metadata.get("negative_stance", ""))
        debate_topic = str(topic_md.metadata.get("debate_topic", ""))
        debate_topic_full = topic_md.content

        rdata: dict[str, str | int] = {
            "stance": stance or affirmative_stance,
            "affirmative_stance": affirmative_stance,
            "negative_stance": negative_stance,
            "debate_topic": debate_topic,
            "debate_topic_full": debate_topic_full,
            "max_words": self.config.actor.max_words,
            "max_rounds": self.config.actor.max_rounds,
            "current_date": datetime.datetime.now(tzlocal()).strftime(
                "%Y 年 %m 月 %d 日，%H:%M"
            ),
        }
        if self.config.actor.teams.prosecution:
            rdata["affirmative_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/prosecution/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.actor.teams.prosecution
                ]
            )
        if self.config.actor.teams.defense:
            rdata["negative_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/defense/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.actor.teams.defense
                ]
            )
        if self.config.actor.teams.witness:
            rdata["witness_agents"] = ", ".join(
                [
                    f"{self._load_raw_frontmatter('agents/witness/' + agent).get('name') or agent} ({agent})"
                    for agent in self.config.actor.teams.witness
                ]
            )
        if data:
            rdata.update(data)

        return super().load_and_render(filepath, rdata)
