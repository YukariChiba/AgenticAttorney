from typing import Any, Literal, cast

from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

from src.prompts.engine import TemplateEngine
from src.types.config import AppConfig


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
            common_sysmsg = self.template_engine.load_and_render(
                common_sysmsg_path
            ).content
            final_system_msg = f"{common_sysmsg}\n\n{system_msg}"

        kwargs: dict[str, Any] = {
            "name": agent_name,
            "system_message": final_system_msg,
            "description": agent_desc,
            "model_client": self.model_client,
            "model_client_stream": True,
        }

        if tools:
            kwargs["tools"] = cast(list[Any], tools)
            kwargs["reflect_on_tool_use"] = False
            kwargs["max_tool_iterations"] = self.config.debate.max_tool_iterations

        return AssistantAgent(**kwargs)

    def create_debate_agent(
        self,
        agent_name: str,
        side: Literal["prosecution", "defense"],
        tools: list[Any] | None = None,
    ) -> AssistantAgent:
        stance = (
            self.config.affirmative_stance
            if side == "prosecution"
            else self.config.negative_stance
        )
        md = self.template_engine.load_and_render(
            f"agents/{side}/{agent_name}", {"stance": stance}
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
