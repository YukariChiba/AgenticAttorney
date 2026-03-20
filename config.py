import os
from dataclasses import dataclass
from typing import Any

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.models import ChatCompletionClient, ModelFamily
from dotenv import load_dotenv

from mdfiles import load_md

load_dotenv()

model_config: dict[str, Any] = {
    "provider": "OpenAIChatCompletionClient",
    "config": {
        "model": os.getenv("MODEL_API_NAME"),
        "base_url": os.getenv("MODEL_API_URL"),
        "api_key": os.getenv("MODEL_API_KEY"),
        "timeout": 1200,
        "temperature": 0.9,
        "parallel_tool_calls": True,
        "model_info": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.UNKNOWN,
            "structured_output": True,
        },
    },
}

model_client: ChatCompletionClient = ChatCompletionClient.load_component(model_config)

topic_config = "theseus"

topic_md = load_md(f"topics/{topic_config}")

debate_topic: str = str(topic_md.metadata.get("debate_topic"))
debate_topic_full: str = topic_md.content
affirmative_stance: str = str(topic_md.metadata.get("affirmative_stance"))
negative_stance: str = str(topic_md.metadata.get("negative_stance"))


@dataclass(frozen=True)
class TeamsConfig:
    A: list[str]
    N: list[str]
    J: str
    JF: str
    W: list[str]
    JR: str | None


teams: TeamsConfig = TeamsConfig(
    A=["Manfred_von_Karma", "Miles_Edgeworth", "Godot"],
    N=["Phoenix_Wright", "Apollo_Justice", "Mia_Fey"],
    J="Judge",
    JF="Judge_Final",
    W=[
        "Dick_Gumshoe",
        "Ema_Skye",
        "Larry_Butz",
        "Lotta_Hart",
    ],
    JR="Jury",
)

max_words: int = 300
max_rounds: int = 8

max_buffer: int = max_rounds * 2

termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(
    max_messages=max_rounds * 2
)
