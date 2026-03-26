import contextlib
from typing import TypeAlias

from autogen_ext.tools.mcp import (
    SseMcpToolAdapter,
    StdioMcpToolAdapter,
    StdioServerParams,
    StreamableHttpMcpToolAdapter,
    create_mcp_server_session,
    mcp_server_tools,
)

from src.types.actor.config import McpServerConfig

McpToolAdapter: TypeAlias = (
    StdioMcpToolAdapter | SseMcpToolAdapter | StreamableHttpMcpToolAdapter
)


class McpToolManager:
    def __init__(self, server_configs: list[McpServerConfig] | None = None) -> None:
        self.server_configs = server_configs or []
        self.stack = contextlib.AsyncExitStack()
        self.all_tools: list[McpToolAdapter] = []

    async def setup(self) -> list[McpToolAdapter]:
        for server_config in self.server_configs:
            params = StdioServerParams(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env,
                read_timeout_seconds=server_config.read_timeout_seconds,
            )
            session = await self.stack.enter_async_context(
                create_mcp_server_session(params)
            )
            await session.initialize()
            tools = await mcp_server_tools(params, session=session)
            self.all_tools.extend(tools)
        return self.all_tools

    async def cleanup(self) -> None:
        await self.stack.aclose()
