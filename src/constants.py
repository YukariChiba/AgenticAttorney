"""项目常量定义 - 统一管理所有路径配置"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
DIRECTOR_DATA_DIR = DATA_DIR / "director"

# Prompts 目录
PROMPTS_DIR = PROJECT_ROOT / "prompts"
TOPICS_DIR = PROMPTS_DIR / "topics"

# 输出目录
LOGS_DIR = PROJECT_ROOT / "logs"

# 缓存目录
CACHE_DIR = PROJECT_ROOT / "cache"

# 具体文件路径
BACKGROUND_JSON = DIRECTOR_DATA_DIR / "background.json"
TAGS_JSON = DIRECTOR_DATA_DIR / "tags.json"


# 确保目录存在
def ensure_directories():
    """确保所有必要的目录存在"""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
