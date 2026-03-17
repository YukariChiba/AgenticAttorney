from typing import Any, cast

import frontmatter
from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from config import (
    affirmative_stance,
    max_buffer,
    max_rounds,
    model_client,
    negative_stance,
    teams,
)
from prompts import load_prompt
from tools import McpToolAdapter

common_sysmsg = load_prompt("common").content


def create_debate_agent(
    agent_name: str, system_msg: str, agent_desc: str, tools: list[McpToolAdapter]
) -> AssistantAgent:
    return AssistantAgent(
        name=agent_name,
        system_message=f"{common_sysmsg}\n{system_msg}",
        description=agent_desc,
        model_client=model_client,
        model_client_stream=True,
        tools=cast(list[Any], tools),
        reflect_on_tool_use=True,
        model_context=BufferedChatCompletionContext(buffer_size=max_buffer),
    )


def create_judge_agent(
    agent_name: str, system_msg: str, agent_desc: str
) -> AssistantAgent:
    return AssistantAgent(
        name=agent_name,
        system_message=system_msg,
        description=agent_desc,
        model_client=model_client,
        model_context=BufferedChatCompletionContext(buffer_size=max_rounds * 2 + 2),
    )


def build_all_agents(
    all_tools: list[McpToolAdapter],
) -> tuple[
    AssistantAgent,
    AssistantAgent,
    AssistantAgent,
    AssistantAgent,
    list[AssistantAgent],
    dict[str, str],
]:
    namemap: dict[str, str] = {}
    all_agents: list[AssistantAgent] = []

    def load_agent(config_name: str, stance: str | None = None) -> AssistantAgent:
        md: frontmatter.Post = load_prompt(f"agents/{config_name}", stance)
        desc = str(md.metadata.get("desc", ""))

        if stance:
            agent = create_debate_agent(config_name, md.content, desc, all_tools)
        else:
            agent = create_judge_agent(config_name, md.content, desc)

        all_agents.append(agent)

        if name := md.metadata.get("name"):
            namemap[config_name] = str(name)

        return agent

    a_agents: list[AssistantAgent] = [
        load_agent(cfg, affirmative_stance) for cfg in teams.A
    ]
    n_agents: list[AssistantAgent] = [
        load_agent(cfg, negative_stance) for cfg in teams.N
    ]

    judge: AssistantAgent = load_agent(teams.J)
    judge_final: AssistantAgent = load_agent(teams.JF)

    return (a_agents[0], n_agents[0], judge, judge_final, all_agents, namemap)
