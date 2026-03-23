from typing import Any, cast

from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
from autogen_core.models import ChatCompletionClient

from src.core.models import AppConfig
from src.types.agent import AgentMetadata, ClerkAgent

from ..prompts.engine import TemplateEngine


class AgentFactory:
    def __init__(
        self,
        config: AppConfig,
        model_client: ChatCompletionClient,
        template_engine: TemplateEngine,
    ) -> None:
        self.config = config
        self.model_client = model_client
        self.template_engine = template_engine

    def _create_base_agent(
        self,
        agent_name: str,
        system_msg: str,
        agent_desc: str,
        tools: list[Any] | None = None,
        common_sysmsg_path: str | None = None,
    ) -> AssistantAgent:
        final_system_msg = system_msg
        if common_sysmsg_path:
            common_sysmsg = self.template_engine.load_content(common_sysmsg_path)
            final_system_msg = f"{system_msg}\n{common_sysmsg}"

        kwargs: dict[str, Any] = {
            "name": agent_name,
            "system_message": final_system_msg,
            "description": agent_desc,
            "model_client": self.model_client,
            "model_client_stream": True,
        }

        if tools:
            kwargs["tools"] = cast(list[Any], tools)
            kwargs["reflect_on_tool_use"] = True

        return AssistantAgent(**kwargs)

    def create_prosecution_agent(
        self, agent_name: str, tools: list[Any] | None = None
    ) -> AssistantAgent:
        md = self.template_engine.load_and_render(
            f"agents/prosecution/{agent_name}",
            {"stance": self.config.affirmative_stance},
        )
        desc = str(md.metadata.get("desc", ""))
        return self._create_base_agent(
            agent_name, md.content, desc, tools, "agents/common/debate"
        )

    def create_defense_agent(
        self, agent_name: str, tools: list[Any] | None = None
    ) -> AssistantAgent:
        md = self.template_engine.load_and_render(
            f"agents/defense/{agent_name}",
            {"stance": self.config.negative_stance},
        )
        desc = str(md.metadata.get("desc", ""))
        return self._create_base_agent(
            agent_name, md.content, desc, tools, "agents/common/debate"
        )

    def create_judge_agent(self, agent_name: str) -> AssistantAgent:
        md = self.template_engine.load_and_render(f"agents/judge/{agent_name}")
        desc = str(md.metadata.get("desc", ""))
        return self._create_base_agent(agent_name, md.content, desc)

    def create_witness_agent(
        self, agent_name: str, tools: list[Any] | None = None
    ) -> AssistantAgent:
        md = self.template_engine.load_and_render(f"agents/witness/{agent_name}")
        desc = str(md.metadata.get("desc", ""))
        return self._create_base_agent(
            agent_name, md.content, desc, tools, "agents/common/witness"
        )

    def create_jury_agent(self, agent_name: str) -> AssistantAgent:
        md = self.template_engine.load_and_render(f"agents/jury/{agent_name}")
        desc = str(md.metadata.get("desc", ""))
        return self._create_base_agent(agent_name, md.content, desc)


class AgentManager:
    def __init__(
        self,
        config: AppConfig,
        factory: AgentFactory,
        tools: list[Any] | None = None,
    ) -> None:
        self.config = config
        self.factory = factory

        self.all_agents: list[BaseChatAgent] = []
        self.metamap: dict[str, AgentMetadata] = {}

        first_prosecution: AssistantAgent | None = None
        first_defense: AssistantAgent | None = None
        judge: AssistantAgent | None = None
        judge_final: AssistantAgent | None = None
        clerk: ClerkAgent = ClerkAgent()

        self.all_agents.append(clerk)

        for agent_name in self.config.teams.prosecution:
            agent = self.factory.create_prosecution_agent(agent_name, tools)
            self._add_agent(agent_name, agent, f"agents/prosecution/{agent_name}")
            if first_prosecution is None:
                first_prosecution = agent

        for agent_name in self.config.teams.defense:
            agent = self.factory.create_defense_agent(agent_name, tools)
            self._add_agent(agent_name, agent, f"agents/defense/{agent_name}")
            if first_defense is None:
                first_defense = agent

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

        if self.config.teams.jury:
            jury = self.factory.create_jury_agent(self.config.teams.jury)
            self._add_agent(
                self.config.teams.jury, jury, f"agents/jury/{self.config.teams.jury}"
            )

        assert first_prosecution is not None
        assert first_defense is not None
        assert judge is not None
        assert judge_final is not None

        self.first_prosecution = first_prosecution
        self.first_defense = first_defense
        self.judge = judge
        self.judge_final = judge_final
        self.clerk = clerk

    def _add_agent(
        self, agent_name: str, agent: AssistantAgent, metadata_path: str
    ) -> None:
        self.all_agents.append(agent)
        try:
            metadata = self.factory.template_engine.load_metadata(metadata_path)
            self.metamap[agent_name] = AgentMetadata(
                name=str(metadata.get("name", "")),
                desc=str(metadata.get("desc", "")),
                objlol=cast(int, metadata.get("objlol", 0)),
            )
        except FileNotFoundError:
            pass
