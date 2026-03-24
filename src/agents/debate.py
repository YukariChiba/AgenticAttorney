from typing import Any, cast

from autogen_agentchat.agents import AssistantAgent, BaseChatAgent

from src.agents.factory import AgentFactory
from src.types.agent import AgentMetadata, ClerkAgent
from src.types.config import AppConfig


class DebateAgentManager:
    def __init__(
        self,
        config: AppConfig,
        factory: AgentFactory,
        tools: list[Any] | None = None,
    ) -> None:
        self.config = config
        self.factory = factory

        self.all_agents: list[BaseChatAgent] = []
        self.prosecution_agents: list[AssistantAgent] = []
        self.defense_agents: list[AssistantAgent] = []
        self.metamap: dict[str, AgentMetadata] = {}

        judge: AssistantAgent | None = None
        judge_final: AssistantAgent | None = None

        for agent_name in self.config.teams.prosecution:
            agent = self.factory.create_debate_agent(
                agent_name, "prosecution", tools or []
            )
            self._add_agent(agent_name, agent, f"agents/prosecution/{agent_name}")
            self.prosecution_agents.append(agent)

        for agent_name in self.config.teams.defense:
            agent = self.factory.create_debate_agent(agent_name, "defense", tools or [])
            self._add_agent(agent_name, agent, f"agents/defense/{agent_name}")
            self.prosecution_agents.append(agent)

        judge = self.factory.create_judge_agent(self.config.teams.judge)
        self._add_agent(
            self.config.teams.judge, judge, f"agents/judge/{self.config.teams.judge}"
        )

        judge_final = self.factory.create_judge_agent(self.config.teams.judge_final)
        self._add_agent(
            self.config.teams.judge_final,
            judge_final,
            f"agents/judge/{self.config.teams.judge_final}",
        )

        for agent_name in self.config.teams.witness:
            agent = self.factory.create_witness_agent(agent_name, tools)
            self._add_agent(agent_name, agent, f"agents/witness/{agent_name}")

        assert judge is not None
        assert judge_final is not None

        self.judge = judge
        self.judge_final = judge_final
        self.clerk = ClerkAgent()
        self.all_agents.append(self.clerk)

    def _add_agent(
        self, agent_name: str, agent: AssistantAgent, metadata_path: str
    ) -> None:
        self.all_agents.append(agent)
        metadata = self.factory.template_engine.load_and_render(metadata_path).metadata
        self.metamap[agent_name] = AgentMetadata(
            name=str(metadata.get("name", "")),
            desc=str(metadata.get("desc", "")),
            objlol=cast(int, metadata.get("objlol", 0)),
        )
