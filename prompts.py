import datetime

import frontmatter
from dateutil.tz import tzlocal

from config import (
    affirmative_stance,
    debate_topic,
    debate_topic_full,
    max_rounds,
    max_words,
    negative_stance,
    teams,
)
from mdfiles import load_frontmatter, load_md_raw

def load_prompt(file: str, stance: str | None = None) -> frontmatter.Post:
    s: str = load_md_raw(file)
    replacements: dict[str, str] = {
        "{stance}": stance or affirmative_stance,
        "{affirmative_stance}": affirmative_stance,
        "{negative_stance}": negative_stance,
        "{debate_topic}": debate_topic,
        "{debate_topic_full}": debate_topic_full,
        "{max_words}": str(max_words),
        "{max_rounds}": str(max_rounds),
        "{current_date}": datetime.datetime.now(tzlocal()).strftime(
            "%Y 年 %m 月 %d 日，%H:%M"
        ),
        "{affirmative_agents}": ", ".join(
            [
                f"{load_frontmatter('agents/debate/' + agent).get('name') or agent} ({agent})"
                for agent in teams.A
            ]
        ),
        "{negative_agents}": ", ".join(
            [
                f"{load_frontmatter('agents/debate/' + agent).get('name') or agent} ({agent})"
                for agent in teams.N
            ]
        ),
        "{witness_agents}": ", ".join(
            [
                f"{load_frontmatter('agents/witness/' + agent).get('name') or agent} ({agent})"
                for agent in teams.W
            ]
        ),
    }
    for key, value in replacements.items():
        s = s.replace(key, value)
    return frontmatter.loads(s)
