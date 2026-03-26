import argparse
import asyncio
import logging
import sys

from src.constants import LOGS_DIR, ensure_directories
from src.core.actor import CourtSession
from src.core.config_loader import load_config
from src.core.director.assets import AssetsManager
from src.core.director.converter import LogConverter
from src.tools.mcp_manager import McpToolManager
from src.types.config import AppConfig


async def run_debate(config: AppConfig):
    mcp_manager = McpToolManager(config.actor.mcp_servers)
    tools = await mcp_manager.setup()
    try:
        session = CourtSession(config, tools)
        await session.start()
        savefile = session.logger.save()
        print(f"记录已保存：{savefile}")
    finally:
        await mcp_manager.cleanup()


async def run_convert(config: AppConfig, logfile: str):
    input_file = LOGS_DIR / f"{logfile}.json"
    output_file = LOGS_DIR / f"{logfile}.objection"

    if not input_file.exists():
        logging.error(f"日志文件不存在: {input_file}")
        logging.info("可用的日志文件:")
        for f in LOGS_DIR.glob("*.json"):
            logging.info(f"  - {f.stem}")
        sys.exit(1)

    logging.info(f"输入文件: {input_file}")
    logging.info(f"输出文件: {output_file}")

    try:
        logging.info("正在获取资源...")
        assets_manager = AssetsManager(config.director.cache_duration)
        assets_manager.fetch_characters()
        assets_manager.fetch_music()
        assets_manager.fetch_sounds()

        num_chars = len(assets_manager._characters) if assets_manager._characters else 0
        num_music = len(assets_manager._music) if assets_manager._music else 0
        num_sounds = len(assets_manager._sounds) if assets_manager._sounds else 0
        logging.info(f"已加载 {num_chars} 个角色")
        logging.info(f"已加载 {num_music} 首音乐")
        logging.info(f"已加载 {num_sounds} 个音效")

        logging.info("正在加载日志文件...")
        temp_converter = LogConverter(assets_manager, [], config)
        logs = temp_converter.load_log_file(str(input_file))
        logging.info(f"找到 {len(logs)} 条日志记录")

        converter = LogConverter(assets_manager, logs, config)

        frames = await converter.process_sequence(logs)
        logging.info(f"生成了 {len(frames)} 帧")

        logging.info("正在保存 director 文件...")
        converter.save_director_file(frames, str(output_file))

        print(f"转换完成：{output_file.absolute()}")

    except KeyboardInterrupt:
        logging.info("用户中断")
        sys.exit(1)
    except Exception as e:
        logging.error(f"发生错误: {e}", exc_info=True)
        sys.exit(1)


def main():
    # 确保目录存在
    ensure_directories()

    # suppress extra logging
    logging.getLogger("autogen_core").setLevel(logging.WARNING)
    logging.getLogger("autogen_contextplus").setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(description="AgenticAttorney")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # debate
    subparsers.add_parser("debate", help="运行法庭辩论")

    # convert
    convert_parser = subparsers.add_parser(
        "convert", help="将辩论日志转换为 objection.lol 剧本"
    )
    convert_parser.add_argument(
        "logfile",
        help="日志文件名（不含 .json 后缀）",
    )

    args = parser.parse_args()

    config = load_config("config.json")

    if args.command == "debate":
        asyncio.run(run_debate(config))
    elif args.command == "convert":
        if not args.logfile:
            convert_parser.error("需要提供日志文件名")
        asyncio.run(run_convert(config, args.logfile))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
