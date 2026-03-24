import asyncio
import logging

from src.core.court import CourtSession
from src.tools.mcp_manager import McpToolManager
from src.types.config import AppConfig


async def main():
    # suppress logging
    logging.getLogger("autogen_core").setLevel(logging.WARNING)
    logging.getLogger("autogen_contextplus").setLevel(logging.WARNING)

    config = AppConfig.load("config.json")
    mcp_manager = McpToolManager(config.mcp_servers)
    tools = await mcp_manager.setup()
    try:
        session = CourtSession(config, tools)
        await session.start()
        savefile = session.logger.save()
        print(f"记录已保存：{savefile}")
    finally:
        await mcp_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
