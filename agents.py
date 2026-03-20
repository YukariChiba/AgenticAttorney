from typing import Any, cast

import frontmatter
from autogen_agentchat.agents import AssistantAgent

from config import (
    affirmative_stance,
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
    )


def create_judge_agent(
    agent_name: str, system_msg: str, agent_desc: str
) -> AssistantAgent:
    return AssistantAgent(
        name=agent_name,
        system_message=system_msg,
        model_client_stream=True,
        description=agent_desc,
        model_client=model_client,
    )


def create_witness_agent(
    agent_name: str, system_msg: str, agent_desc: str, tools: list[McpToolAdapter]
) -> AssistantAgent:
    return AssistantAgent(
        name=agent_name,
        system_message=system_msg,
        description=agent_desc,
        model_client=model_client,
        model_client_stream=True,
        tools=cast(list[Any], tools),
        reflect_on_tool_use=True,
    )


def create_jury_agent(
    agent_name: str, system_msg: str, agent_desc: str
) -> AssistantAgent:
    return AssistantAgent(
        name=agent_name,
        system_message=system_msg,
        model_client_stream=True,
        description=agent_desc,
        model_client=model_client,
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

    def load_agent(config_name: str, agent_type: str = "debate") -> AssistantAgent:
        stance = None
        if agent_type == "prosecution":
            stance = affirmative_stance
        if agent_type == "defense":
            stance = negative_stance
        md: frontmatter.Post = load_prompt(f"agents/{agent_type}/{config_name}", stance)
        desc = str(md.metadata.get("desc", ""))

        if agent_type == "prosecution" or agent_type == "defense":
            agent = create_debate_agent(config_name, md.content, desc, all_tools)
        elif agent_type == "witness":
            agent = create_witness_agent(config_name, md.content, desc, all_tools)
        elif agent_type == "jury":
            agent = create_jury_agent(config_name, md.content, desc)
        else:
            agent = create_judge_agent(config_name, md.content, desc)

        all_agents.append(agent)

        if name := md.metadata.get("name"):
            namemap[config_name] = str(name)

        return agent

    a_agents: list[AssistantAgent] = [
        load_agent(cfg, "prosecution") for cfg in teams.Prosecution
    ]
    n_agents: list[AssistantAgent] = [
        load_agent(cfg, "defense") for cfg in teams.Defense
    ]

    judge: AssistantAgent = load_agent(teams.Judge, "judge")
    judge_final: AssistantAgent = load_agent(teams.JudgeFinal, "judge")

    for witness_cfg in teams.Witness:
        load_agent(witness_cfg, "witness")

    if teams.Jury:
        load_agent(teams.Jury, "jury")

    return (a_agents[0], n_agents[0], judge, judge_final, all_agents, namemap)
