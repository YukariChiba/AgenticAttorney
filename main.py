import asyncio
import logging
import warnings
from typing import Any, cast

from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import SelectorGroupChat

from agents import build_all_agents
from config import (
    model_client,
    termination_condition,
)
from format import Formatter
from prompts import load_prompt
from tools import McpToolManager


async def main():
    logging.getLogger().setLevel(logging.WARNING)
    # suppress: UserWarning: Resolved model mismatch
    warnings.filterwarnings("ignore", category=UserWarning)

    formatter = Formatter()

    formatter.fmtsys("系统初始化...")
    
    mcp_manager = McpToolManager()
    all_tools = await mcp_manager.setup()
    
    A1, N1, Judge, Judge_Final, AllAgents, namemap = build_all_agents(all_tools)
    
    formatter.namemap = namemap

    formatter.fmtsys("赛前准备阶段（双方正在后台查阅卷宗...）")

    async for event in A1.run_stream(
        task=TextMessage(content=load_prompt("prepare").content, source=Judge.name)
    ):
        formatter.fmtmsg(event)
    async for event in N1.run_stream(
        task=TextMessage(content=load_prompt("prepare").content, source=Judge.name)
    ):
        formatter.fmtmsg(event)

    formatter.fmtsys("法庭辩论正式开始")

    debate_team = SelectorGroupChat(
        participants=cast(list[Any], AllAgents),
        model_client=model_client,
        model_client_streaming=True,
        emit_team_events=True,
        termination_condition=termination_condition,
    )

    terminated_by_judge = False

    init_msg = TextMessage(content=load_prompt("init").content, source=Judge.name)
    debate_history = [init_msg]

    async for event in debate_team.run_stream(task=init_msg):
        formatter.fmtmsg(event)
        if isinstance(event, TextMessage):
            debate_history.append(event)
            if "TERMINATE" in event.content:
                terminated_by_judge = True

    if not terminated_by_judge:
        formatter.fmtsys("宣判环节")
        final_task = TextMessage(
            content=load_prompt("final").content, source=Judge_Final.name
        )
        formatter.fmtmsg(final_task)
        async for event in Judge_Final.run_stream(
            task=debate_history + [final_task], output_task_messages=False
        ):
            formatter.fmtmsg(event)
            
    await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
