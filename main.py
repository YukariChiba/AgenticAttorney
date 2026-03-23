import asyncio

from src.session import CourtSession
from src.core.models import AppConfig
from src.tools.mcp_manager import McpToolManager


async def main():
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
