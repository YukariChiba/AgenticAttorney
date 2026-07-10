import contextlib
from typing import TypeAlias

from autogen_ext.tools.mcp import (
    SseMcpToolAdapter,
    StdioMcpToolAdapter,
    StdioServerParams,
    StreamableHttpMcpToolAdapter,
    StreamableHttpServerParams,
    create_mcp_server_session,
    mcp_server_tools,
)

from src.types.actor.config import (
    HttpMcpServerConfig,
    McpServerConfig,
    StdioMcpServerConfig,
)

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
            if isinstance(server_config, StdioMcpServerConfig):
                env = (server_config.env or {}).copy()
                # Python logging
                env["LOGLEVEL"] = "WARNING"
                env["LOG_LEVEL"] = "WARNING"
                env["PYTHONWARNINGS"] = "ignore"
                # MCP SDK
                env["MCP_LOG_LEVEL"] = "WARNING"
                env["MCP_LOGGING_LEVEL"] = "WARNING"
                # HTTPX
                env["HTTPX_LOG_LEVEL"] = "WARNING"
                # Node.js
                env["NODE_NO_WARNINGS"] = "1"
                params = StdioServerParams(
                    command=server_config.command,
                    args=server_config.args,
                    env=env,
                    read_timeout_seconds=server_config.read_timeout_seconds,
                )
            elif isinstance(server_config, HttpMcpServerConfig):
                params = StreamableHttpServerParams(
                    url=server_config.url,
                    headers=server_config.headers,
                    timeout=server_config.timeout,
                    sse_read_timeout=server_config.sse_read_timeout,
                    terminate_on_close=server_config.terminate_on_close,
                )
            else:
                continue
            session = await self.stack.enter_async_context(
                create_mcp_server_session(params)
            )
            await session.initialize()
            tools = await mcp_server_tools(params, session=session)
            self.all_tools.extend(tools)
        return self.all_tools

    async def cleanup(self) -> None:
        await self.stack.aclose()
