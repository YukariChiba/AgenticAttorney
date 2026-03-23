from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core.models import ChatCompletionClient

from .models import (
    DebateSettingsConfig,
    ModelConfig,
)


def load_model_client(config: ModelConfig) -> ChatCompletionClient:
    model_config_dict = config.to_component_config()
    return ChatCompletionClient.load_component(model_config_dict)


def create_termination_condition(
    debate_settings: DebateSettingsConfig,
) -> TerminationCondition:
    return TextMentionTermination("TERMINATE") | MaxMessageTermination(
        max_messages=debate_settings.max_rounds * 2
    )
