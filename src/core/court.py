import asyncio
from typing import Any, cast

from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_contextplus.extension.context import (
    buffered_summary_chat_completion_context_builder,
)
from autogen_core.models import ChatCompletionClient

from src.prompts.debate import DebateTemplateEngine
from src.tools.mcp_manager import McpToolAdapter
from src.types.config import AppConfig

from ..agents.debate import AgentFactory, DebateAgentManager
from ..outputs.console import ConsoleFormatter
from ..outputs.logfile import LogfileFormatter
from ..prompts.engine import TemplateEngine


class CourtSession:
    def __init__(
        self, config: AppConfig, tools: list[McpToolAdapter] | None = None
    ) -> None:
        self.config = config
        self.model_client: ChatCompletionClient = ChatCompletionClient.load_component(
            self.config.model.to_component_config()
        )
        self.template_engine: TemplateEngine = DebateTemplateEngine(self.config)
        self.termination_condition: TerminationCondition = TextMentionTermination(
            "TERMINATE"
        ) | MaxMessageTermination(max_messages=self.config.debate.max_rounds * 2)

        self.agent_manager = DebateAgentManager(
            self.config,
            AgentFactory(self.config, self.model_client, self.template_engine),
            tools,
        )

        self.logger = LogfileFormatter(self.config, self.agent_manager.metamap)
        self.formatter = ConsoleFormatter(self.config, self.agent_manager.metamap)
        self.debate_team: SelectorGroupChat

    async def run_preparation(self) -> None:
        self.formatter.print_system("赛前准备阶段（双方正在后台查阅卷宗...）")

        prepare_prompt = self.template_engine.load_and_render("prepare").content
        prepare_message = TextMessage(
            content=prepare_prompt, source=self.agent_manager.judge.name
        )
        self.formatter.print_event(prepare_message)

        debate_agents = (
            self.agent_manager.prosecution_agents + self.agent_manager.defense_agents
        )
        queue: asyncio.Queue[Any] = asyncio.Queue()
        lock = asyncio.Lock()

        async def consume_events(agent: Any) -> None:
            async for event in agent.run_stream(
                task=prepare_message, output_task_messages=False
            ):
                await queue.put(event)
            await queue.put(None)

        async def async_print_events() -> None:
            pending = len(debate_agents)
            while pending > 0:
                event = await queue.get()
                if event is None:
                    pending -= 1
                else:
                    async with lock:
                        self.formatter.print_event(event)

        consumer = asyncio.create_task(async_print_events())
        await asyncio.gather(*[consume_events(agent) for agent in debate_agents])
        await consumer

    async def run_debate(self) -> bool:
        self.formatter.print_system("法庭辩论正式开始")

        self.agent_manager.clerk.conv_func = lambda s: str(
            self.agent_manager.metamap.get(s, {}).get("name", s)
        )

        self.debate_team = SelectorGroupChat(
            participants=cast(list[Any], self.agent_manager.all_agents),
            model_client=self.model_client,
            model_client_streaming=True,
            selector_func=self.agent_manager.clerk.selector,
            selector_prompt=self.template_engine.load_and_render("selector").content,
            model_context=buffered_summary_chat_completion_context_builder(
                max_messages=self.config.debate.max_context,
                model_client=self.model_client,
                system_message=self.template_engine.load_and_render("summary").content,
                summary_start=self.config.debate.summary_start,
                summary_end=-self.config.debate.summary_end,
                summary_format="先前的辩论记录已由书记员总结:\n\n {summary}",
            ),
            emit_team_events=True,
            termination_condition=self.termination_condition,
        )

        terminated_by_judge = False
        init_msg = TextMessage(
            content=self.template_engine.load_and_render("init").content,
            source=self.agent_manager.judge.name,
        )

        async for event in self.debate_team.run_stream(task=init_msg):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.logger.log_event(event)
                if "TERMINATE" in event.content:
                    terminated_by_judge = True

        return terminated_by_judge

    async def run_verdict(self) -> None:
        self.formatter.print_system("宣判环节")
        final_task = TextMessage(
            content=self.template_engine.load_and_render("final").content,
            source=self.agent_manager.judge.name,
        )

        self.agent_manager.clerk.set_next_speaker(self.agent_manager.judge_final.name)
        async for event in self.debate_team.run_stream(task=final_task):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.logger.log_event(event)

    async def start(self) -> None:
        await self.run_preparation()
        terminated_by_judge = await self.run_debate()
        if not terminated_by_judge:
            await self.run_verdict()
