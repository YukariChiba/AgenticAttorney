from typing import Any, Literal, cast

from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core.models import ChatCompletionClient

from src.core.config_loader import load_topic_md
from src.prompts.engine import TemplateEngine
from src.tools.memory import AgentMemory
from src.types.config import AppConfig
from src.types.director.frames import FrameList


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
            kwargs["max_tool_iterations"] = self.config.actor.max_tool_iterations

        return AssistantAgent(**kwargs)

    def create_debate_agent(
        self,
        agent_name: str,
        side: Literal["prosecution", "defense"],
        tools: list[Any] | None = None,
    ) -> AssistantAgent:
        topic_md = load_topic_md(self.config.actor.topic)
        affirmative_stance = str(topic_md.metadata.get("affirmative_stance", ""))
        negative_stance = str(topic_md.metadata.get("negative_stance", ""))
        stance = affirmative_stance if side == "prosecution" else negative_stance
        md = self.template_engine.load_and_render(
            f"agents/{side}/{agent_name}", {"stance": stance}
        )
        desc = str(md.metadata.get("desc", ""))

        memory = AgentMemory()
        agent_tools = list(tools) if tools else []
        agent_tools.extend(memory.tools)

        return self._create_base_agent(
            agent_name, md.content, desc, agent_tools, "agents/common/debate"
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

    def create_objection_agent(self, system_msg: str) -> AssistantAgent:
        return AssistantAgent(
            name="ObjectionDirector",
            system_message=system_msg,
            description="法庭剧本导演，将辩论日志转换为逆转裁判风格的剧本",
            model_client=self.model_client,
            model_client_stream=True,
            reflect_on_tool_use=True,
            output_content_type=FrameList,
            model_context=BufferedChatCompletionContext(
                buffer_size=self.config.director.buffer_size
            ),
        )
