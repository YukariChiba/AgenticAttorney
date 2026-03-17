import contextlib
import os
from typing import TypeAlias

from autogen_ext.tools.mcp import (
    SseMcpToolAdapter,
    StdioMcpToolAdapter,
    StdioServerParams,
    StreamableHttpMcpToolAdapter,
    create_mcp_server_session,
    mcp_server_tools,
)

McpToolAdapter: TypeAlias = (
    StdioMcpToolAdapter | SseMcpToolAdapter | StreamableHttpMcpToolAdapter
)

servers = [
    StdioServerParams(
        command="uvx",
        args=["wikipedia-mcp", "--language", "zh-hans"],
        read_timeout_seconds=20,
    ),
    StdioServerParams(
        command="npx",
        args=["-y", "@jharding_npm/mcp-server-searxng"],
        env={"SEARXNG_INSTANCES": os.getenv("SEARXNG_INSTANCES") or ""},
        read_timeout_seconds=20,
    ),
    StdioServerParams(
        command="uvx", args=["arxiv-mcp-server"], read_timeout_seconds=20
    ),
    StdioServerParams(
        command="uvx", args=["mcp-server-fetch"], read_timeout_seconds=20
    ),
]


class McpToolManager:
    def __init__(self):
        self.stack = contextlib.AsyncExitStack()
        self.all_tools: list[McpToolAdapter] = []

    async def setup(self) -> list[McpToolAdapter]:
        for params in servers:
            session = await self.stack.enter_async_context(
                create_mcp_server_session(params)
            )
            await session.initialize()
            tools = await mcp_server_tools(params, session=session)
            self.all_tools.extend(tools)
        return self.all_tools

    async def cleanup(self):
        await self.stack.aclose()
