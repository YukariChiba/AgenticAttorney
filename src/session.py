from typing import Any, cast

from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_contextplus.extension.context import (
    buffered_summary_chat_completion_context_builder,
)
from autogen_core.models import ChatCompletionClient

from src.core.models import AppConfig
from src.tools.mcp_manager import McpToolAdapter

from .agents.manager import AgentFactory, AgentManager
from .core.config import create_termination_condition, load_model_client
from .prompts.engine import TemplateEngine
from .tools.logger import DebateLogger
from .ui.formatter import ConsoleFormatter


class CourtSession:
    def __init__(
        self, config: AppConfig, tools: list[McpToolAdapter] | None = None
    ) -> None:
        self.config = config

        self.model_client: ChatCompletionClient = load_model_client(self.config.model)
        self.template_engine: TemplateEngine = TemplateEngine(self.config)
        self.termination_condition: TerminationCondition = create_termination_condition(
            self.config.debate
        )

        self.agent_manager = AgentManager(
            self.config,
            AgentFactory(self.config, self.model_client, self.template_engine),
            tools,
        )

        self.FirstProsecution = self.agent_manager.first_prosecution
        self.FirstDefense = self.agent_manager.first_defense
        self.Judge = self.agent_manager.judge
        self.Judge_Final = self.agent_manager.judge_final
        self.AllAgents = self.agent_manager.all_agents
        self.metamap = self.agent_manager.metamap

        self.logger = DebateLogger(self.config, self.metamap)
        self.formatter = ConsoleFormatter(self.config, self.metamap)
        self.debate_history: list[TextMessage] = []

    async def run_preparation(self) -> None:
        self.formatter.print_system("赛前准备阶段（双方正在后台查阅卷宗...）")

        prepare_prompt = self.template_engine.load_content("prepare")
        prepare_message = TextMessage(content=prepare_prompt, source=self.Judge.name)
        self.formatter.print_event(prepare_message)
        self.logger.log_event(prepare_message)

        async for event in self.FirstProsecution.run_stream(
            task=prepare_message, output_task_messages=False
        ):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.logger.log_event(event)

        async for event in self.FirstDefense.run_stream(
            task=prepare_message, output_task_messages=False
        ):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.logger.log_event(event)

    async def run_debate(self) -> bool:
        self.formatter.print_system("法庭辩论正式开始")

        debate_team = SelectorGroupChat(
            participants=cast(list[Any], self.AllAgents),
            model_client=self.model_client,
            model_client_streaming=True,
            selector_prompt=self.template_engine.load_content("selector"),
            model_context=buffered_summary_chat_completion_context_builder(
                max_messages=self.config.debate.max_context,
                summary_end=self.config.debate.summary_context,
                model_client=self.model_client,
                system_message="总结之前的辩论内容，体现出发言轮次，要求语气完全中立，不得有任何多余的情感。",
                summary_format="先前的辩论记录已由书记员总结:\n\n {summary}",
            ),
            emit_team_events=True,
            termination_condition=self.termination_condition,
        )

        terminated_by_judge = False
        init_msg = TextMessage(
            content=self.template_engine.load_content("init"), source=self.Judge.name
        )
        self.debate_history = [init_msg]

        async for event in debate_team.run_stream(task=init_msg):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.debate_history.append(event)
                self.logger.log_event(event)
                if "TERMINATE" in event.content:
                    terminated_by_judge = True

        return terminated_by_judge

    async def run_verdict(self) -> None:
        self.formatter.print_system("宣判环节")
        final_task = TextMessage(
            content=self.template_engine.load_content("final"),
            source=self.Judge_Final.name,
        )
        self.formatter.print_event(final_task)
        async for event in self.Judge_Final.run_stream(
            task=self.debate_history + [final_task], output_task_messages=False
        ):
            self.formatter.print_event(event)
            if isinstance(event, TextMessage):
                self.logger.log_event(event)

    async def start(self) -> None:
        await self.run_preparation()
        terminated_by_judge = await self.run_debate()
        if not terminated_by_judge:
            await self.run_verdict()
